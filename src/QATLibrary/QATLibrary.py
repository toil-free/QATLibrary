from __future__ import print_function

import csv
import json
import re
import requests
import pprint

from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from robot.api.deco import keyword
from requests import Request, Session
from jsonschema import validate, exceptions

from .TLSAdapter import TLSAdapter


class QATLibrary(object):
    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    HEADER_VAR_EXP = re.compile(r"\$\{\{.*?\}\}")

    # init session
    session = Session()
    session.mount('https://', TLSAdapter())

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.current_suite = None

        self.builtin = BuiltIn()
        self.base_url = BuiltIn().get_variable_value(name='${base_url}', default='localhost')
        self.timeout = BuiltIn().get_variable_value(name='${timeout}', default=10)
        self.allow_redirects = BuiltIn().get_variable_value(name='${allow_redirects}', default=True)
        self.stream = BuiltIn().get_variable_value(name='${stream}', default=False)

        self.verify = BuiltIn().get_variable_value('${tls.verify_server_cert}', default=True)
        self.certificate = BuiltIn().get_variable_value('${tls.certificate}', default=None)
        self.private_key = BuiltIn().get_variable_value('${tls.private_key}', default=None)
        self.proxies = BuiltIn().get_variable_value('${proxies}', default={})

    def _start_suite(self, suite, result):
        self.current_suite = suite

    @keyword('QAT Dynamic Tests Setup')
    def qat_dynamic_tests_setup(self, csv_file, encoding='utf-8', kwname=None, *args):
        data = self.__generate_dict_data_from_csv(csv_file=csv_file, encoding=encoding)

        try:
            tc = self.current_suite.tests.create(name='Setup Global Test Variables',
                                                 tags='SYSTEM',
                                                 doc='Sets up injectable variables if required')
            tc.body.create_keyword(name='Setup Global Vars', args=[data])

            for i, test_case in enumerate(data, 0):
                if test_case['execute'] not in ['N', 'False', 'false']:
                    tc = self.current_suite.tests.create(name=test_case['testName'] or 'Untitled Test',
                                                         tags=self.__setup_test_tags(test_case),
                                                         doc=self.__setup_test_documentation(test_case))
                    tc.body.create_keyword(name='Data Driven HTTP Request',
                                           args=["${data}" + f'[{i}]'])

                    if kwname is not None:
                        tc.body.create_keyword(name=kwname, args=args)
            logger.info('Dynamic Tests Creation Successful!')
        except Exception as e:
            logger.error(e)
            raise Exception('Dynamic Tests creation failed!')

    @keyword
    def setup_global_vars(self, data):
        # setup data source
        self.builtin.set_global_variable('${data}', data)

        # set bearer token if configured
        if self.builtin.get_variable_value('${bearer_auth}'):
            bearer_token = requests.post(
                url=self.builtin.get_variable_value('${bearer_auth.token_url}'),
                data=self.builtin.get_variable_value('${bearer_auth.payload}'),
                proxies=self.proxies,
                allow_redirects=self.allow_redirects,
                stream=self.stream,
                timeout=self.timeout,
                cert=(self.builtin.get_variable_value('${bearer_auth.tls.private_key}'),
                      self.builtin.get_variable_value('${bearer_auth.tls.key}')),
                verify=self.builtin.get_variable_value('${bearer_auth.tls.verify_server_cert}', True)
            ).json()['access_token']
            self.builtin.set_global_variable('${BEARER_AUTH}', {'Authorization': f'Bearer {bearer_token}'})

    @keyword('Data Driven HTTP Request')
    def qat_data_driven_http_request(self, data):
        logger.debug('Raw Test Data: ' + json.dumps(data, indent=2))
        logger.debug('Preparing HTTP Request..')
        prepped = self.session.prepare_request(Request(method=data['reqType'].upper(),
                                                       url=self.__set_url(data),
                                                       headers=self.__set_headers(data),
                                                       params=self.__set_params(data),
                                                       data=self.__set_payload(data),
                                                       cookies=self.__set_cookies(data)))
        self.__log_prepped_request(prepped, data)
        response = self.session.send(prepped,
                                     allow_redirects=self.allow_redirects,
                                     stream=self.stream,
                                     timeout=self.timeout,
                                     cert=self.__set_ssl_cert(),
                                     proxies=self.__set_proxy(),
                                     verify=self.__verify_server_cert())

        self.__log_response(response)
        self.__assert_response(response, data)

    """ Setup Configurations """

    @staticmethod
    def __generate_dict_data_from_csv(csv_file, encoding='utf-8'):
        """ Takes CSV file. Default encoding for CSV is utf-8,
        override the correct encoding while invoking this method."""
        data = []

        with open(csv_file, encoding=encoding) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data.append(row)
        return data

    @staticmethod
    def __setup_test_documentation(test_case):
        if test_case['documentation'] and test_case['testId']:
            return '[' + test_case['testId'] + '] ' + test_case['documentation']
        else:
            return test_case['documentation'] or ''

    @staticmethod
    def __setup_test_tags(test_case):
        if test_case['tags']:
            return test_case['tags'].split(',')
        else:
            return ['REST API', 'QAT']

    """ Setup Request Payload """

    @staticmethod
    def __set_payload(data):
        if data['reqPayload']:
            return data['reqPayload']
        return None

    """ Setup Request URL """

    def __set_url(self, data):
        url = (data['protocol'] or 'http').lower() + '://' + \
              self.builtin.get_variable_value('${base_url}', default='localhost')
        if data['port']:
            url += ':' + data['port']
        url += data['endPoint']
        return url

    """ Setup Headers """

    def __set_headers(self, data):
        # add bearer auth if available
        global_headers = self.builtin.get_variable_value('${BEARER_AUTH}', {})

        # process global headers
        config_headers = self.builtin.get_variable_value('${headers}', {})
        if config_headers:
            for k, v in config_headers.items():
                global_headers[k] = eval(re.sub(r'\$\{\{(.*?)\}\}', r'\1', v)) if self.HEADER_VAR_EXP.search(v) else v

        # check for user defined headers
        usr_def_headers = self.__get_dict(data['reqHeaders'])
        if usr_def_headers:
            return dict(global_headers.items() | usr_def_headers.items())
        return global_headers

    """ Setup Request Parameters """

    def __set_params(self, data):
        return self.__get_dict(data['reqParams'])

    """ Setup Headers """

    def __set_cookies(self, data):
        return self.__get_dict(data['reqCookies'])

    """ Setup SSL Certs """

    def __set_ssl_cert(self):
        if self.certificate and self.private_key:
            return self.certificate, self.private_key
        if self.certificate:
            return self.certificate, None
        else:
            return None

    """ Configure Verify SSL Certs """

    def __verify_server_cert(self):
        if self.verify in ['True', 'true', 'yes']:
            return True
        if self.verify:
            return self.verify
        else:
            return False

    """ Configure Proxies """

    def __set_proxy(self):
        return self.proxies

    """ Configure Verify SSL Certs """

    def __verify_ssl_cert(self):
        if self.builtin.get_variable_value('${verify_ssl_cert}') in ['True', 'true', 'yes']:
            return True
        if self.builtin.get_variable_value('${verify_ssl_cert}') is not None:
            return self.builtin.get_variable_value('${verify_ssl_cert}')
        else:
            return False

    """ Verify Response """

    def __assert_response(self, response, data):
        err = {'errors': []}
        self.__verify_http_status_code(response, data)
        self.__validate_json_schema(response, data, err['errors'])
        self.__assert_response_body(response, data, err['errors'])
        self.__assert_headers(response, data, err['errors'])
        self.__assert_sla(response, data, err['errors'])

        if err['errors']:
            raise AssertionError(pprint.pformat(err, indent=2))

    """ Get JSON String to Dict """

    @staticmethod
    def __get_dict(json_str, default=None):
        if bool(json_str):
            return json.loads(json_str)
        return default

    """ Get list items from String or JSON. Only takes values from { "values": [] } or comma separated strings """

    @staticmethod
    def __get_values_from_json_or_string(data, key, delimeter=None):
        try:
            return json.loads(data[key])['values'] or []
        except (KeyError, json.decoder.JSONDecodeError) as e:
            logger.trace(e)
            return data[key].split(delimeter) or []

    """ Verify Status Code """

    @staticmethod
    def __verify_http_status_code(response, data):
        expected_http_status = int(data['statusCode']) or 200
        if response.status_code != expected_http_status:
            raise AssertionError("Expected status code: " + data['statusCode'] +
                                 " but actual status code: " + str(response.status_code))
        logger.info('Received Expected HTTP Status Code')

    """ Validate JSON Schema """

    @staticmethod
    def __validate_json_schema(response, data, err):
        if data['jsonSchema']:
            try:
                schema = json.loads(data['jsonSchema'])
            except Exception as e:
                raise Exception('Error while loading JSON Schema. Error: ' + str(e))

            try:
                validate(instance=json.loads(response.text), schema=schema)
                logger.info('JSON Schema validation successful')
            except exceptions.SchemaError as e:
                raise Exception('Invalid JSON Schema. Error: ' + str(e))
            except exceptions.ValidationError as e:
                logger.error(e)
                raise AssertionError('JSON Schema validation failed')

        else:
            logger.warn("No JSON Schema present. Skipping JSON schema validation!")

    """ Validate Response """

    def __assert_response_body(self, response, data, err):
        if data['rspShouldContain'] or data['rspShouldNotContain']:
            logger.info('Running Response Body Assertions..')

            if data['rspShouldContain']:
                valid_contents = self.__get_values_from_json_or_string(data=data,
                                                                       key='rspShouldContain',
                                                                       delimeter=',')
                for content in valid_contents:
                    if not content.strip() in response.text:
                        err.append('Response body does not contain expected: ' + content.strip())

            if data['rspShouldNotContain']:
                invalid_contents = self.__get_values_from_json_or_string(data=data,
                                                                         key='rspShouldNotContain',
                                                                         delimeter=',')
                for content in invalid_contents:
                    if content.strip() in response.text:
                        err.append('Response body contains unexpected: ' + content.strip())

        else:
            logger.info('Skipping Response Body Assertions')

    """ Validate Response Headers """

    def __assert_headers(self, response, data, err):
        expected_headers = self.__get_dict(data['rspHeadersShouldContain'], default={})
        unexpected_headers = self.__get_dict(data['rspHeadersShouldNotContain'], default={})

        if expected_headers or unexpected_headers:
            logger.info('Running Response Headers assertions..')
            if not all(header in response.headers.items() for header in expected_headers.items()):
                logger.error(pprint.pformat(response.headers)
                             + ' Does not contain one or more expected headers: '
                             + pprint.pformat(expected_headers))
                err.append('Response Headers missing expected value(s)')

            if any(header in response.headers.items() for header in unexpected_headers.items()):
                logger.error(pprint.pformat(response.headers)
                             + ' contains one or more unexpected headers: '
                             + pprint.pformat(unexpected_headers))
                err.append('Response Headers contains unexpected value(s)')
        else:
            logger.info('Skipping Response Headers Assertion')

    """ Validate Response SLA """

    @staticmethod
    def __assert_sla(response, data, err):
        if data['rspSLA']:
            rsp_sla = float(data['rspSLA'])
            rsp_time = response.elapsed.total_seconds() * 1000
            if rsp_sla < rsp_time:
                err.append(
                    'Expected Response SLA: ' + str(rsp_sla) + '(ms) but actual was: ' + str(rsp_time) + '(ms)')
            else:
                logger.info('Response SLA Validation Successful')
        else:
            logger.info("Response SLA not configured. Skipping validation.")

    """ Log Request """

    def __log_prepped_request(self, prepped, data):
        body = None
        if prepped.body:
            try:
                body = prepped.body
            except AttributeError:
                body = self.__set_payload(data)
        headers = '\n'.join(['{}: {}'.format(*hv) for hv in prepped.headers.items()])
        logger.info(f"""\
==================================================================================
REQUEST DETAILS:
----------------------------------------------------------------------------------
Method: {prepped.method} HTTP/1.1
URL: {prepped.url}
Timeout: {self.timeout}
Allow Redirects: {self.allow_redirects}
Stream: {self.stream}
Verify Server Cert: {self.verify}
SSL Certificate: {self.certificate}
SSL Private Key: {self.private_key}
Proxies: {self.proxies}
----------------------------------------------------------------------------------
[Request Headers]
----------------------------------------------------------------------------------
{headers}
----------------------------------------------------------------------------------
[Request Body]
----------------------------------------------------------------------------------
{body}
==================================================================================
""")

    """ Log Response """

    @staticmethod
    def __log_response(response):
        rsp_headers = '\n'.join(['{}: {}'.format(*hv) for hv in response.headers.items()])
        logger.info(f"""\
==================================================================================
RESPONSE DETAILS:
----------------------------------------------------------------------------------
Status: {response.status_code} {response.reason}
Time: {response.elapsed.total_seconds() * 1000} ms
Encoding: {response.encoding}
IsRedirect: {response.is_redirect}
Size: {len(response.content)}
History: {response.history}
----------------------------------------------------------------------------------
[Response Headers]
----------------------------------------------------------------------------------
{rsp_headers}
----------------------------------------------------------------------------------
[Response Body]
----------------------------------------------------------------------------------
{response.text}
==================================================================================
""")


globals()[__name__] = QATLibrary
