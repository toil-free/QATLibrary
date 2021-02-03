from __future__ import print_function
import csv
import json
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from robot.api.deco import keyword
import requests
from requests import Request, Session
from requests.auth import HTTPDigestAuth
from jsonschema import validate, exceptions
import pprint

import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

class QATLibrary(object):
    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.current_suite = None

        self.builtin = BuiltIn()
        self.timeout = BuiltIn().get_variable_value(name='${timeout}', default=10)
        self.allow_redirects = BuiltIn().get_variable_value(name='${allow_redirects}', default=True)
        self.stream = BuiltIn().get_variable_value(name='${stream}', default=False)
        self.proxy = BuiltIn().get_variable_value(name='${proxy}', default=None)
        self.authUser = BuiltIn().get_variable_value(name='${authUser}', default=None)
        self.authPass = BuiltIn().get_variable_value(name='${authPass}', default=None)
        self.oauth1_app_key = BuiltIn().get_variable_value(name='${oauth1_app_key}', default=None)
        self.oauth1_app_secret = BuiltIn().get_variable_value(name='${oauth1_app_secret}', default=None)
        self.oauth1_user_token = BuiltIn().get_variable_value(name='${oauth1_user_token}', default=None)
        self.oauth1_user_token_secret = BuiltIn().get_variable_value(name='${oauth1_user_token_secret}', default=None)
        self.verify = BuiltIn().get_variable_value('${verify_server_cert}', default=True)
        self.certificate = BuiltIn().get_variable_value('${certificate}', default=None)
        self.private_key = BuiltIn().get_variable_value('${private_key}', default=None)
        self.http_proxy = BuiltIn().get_variable_value('${http_proxy}', default=None)
        self.https_proxy = BuiltIn().get_variable_value('${https_proxy}', default=None)

    def _start_suite(self, suite, result):
        self.current_suite = suite

    @keyword('QAT Dynamic Tests Setup')
    def qat_dynamic_tests_setup(self, csvFile, encoding='utf-8', kwname=None, *args):
        data = self.__generate_dict_data_from_csv(csvFile=csvFile, encoding=encoding)

        try:
            for testCase in data:
                if testCase['execute'] not in ['N', 'False', 'false']:
                    tc = self.current_suite.tests.create(name=testCase['testName'] or 'Untitled Test',
                                                         tags=self.__setup_test_tags(testCase),
                                                         doc=self.__setup_test_documentation(testCase))
                    tc.keywords.create(name='Data Driven HTTP Request',
                                       args=[testCase])

                    if kwname is not None:
                        tc.keywords.create(name=kwname, args=args)
            logger.info('Dynamic Tests Creation Successful!')
        except Exception as e:
            logger.error(e)
            raise Exception('Dynamic Tests creation failed!')

    @keyword('Data Driven HTTP Request')
    def qat_data_driven_http_request(self, data):
        logger.debug('Raw Test Data: ' + json.dumps(data, indent=2))
        session = Session()
        session.mount('https://', TLSAdapter())

        logger.debug('Preparing HTTP Request..')
        prepped = session.prepare_request(Request(method=data['reqType'].upper(),
                                                  url=self.__set_url(data),
                                                  headers=self.__set_headers(data),
                                                  params=self.__set_params(data),
                                                  data=self.__set_payload(data),
                                                  cookies=self.__set_cookies(data),
                                                  auth=self.__set_auth(data)))
        self.__log_prepped_request(prepped, data, encoding='utf-8')
        response = session.send(prepped,
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
    def __generate_dict_data_from_csv(csvFile, encoding='utf-8'):
        """ Takes CSV file. Default encoding for CSV is utf-8,
        override the correct encoding while invoking this method."""
        data = []

        with open(csvFile, encoding=encoding) as csvFile:
            csv_reader = csv.DictReader(csvFile)
            for row in csv_reader:
                data.append(row)
        return data

    @staticmethod
    def __setup_test_documentation(testCase):
        if testCase['documentation'] and testCase['testId']:
            return '[' + testCase['testId'] + '] ' + testCase['documentation']
        else:
            return testCase['documentation'] or ''

    @staticmethod
    def __setup_test_tags(testCase):
        if testCase['tags']:
            return testCase['tags'].split(',')
        else:
            return ['REST API', 'QAT']

    def __set_auth(self, data):
        if data['authType'].lower() == 'basic':
            return (self.builtin.get_variable_value('${authUser}'),
                    self.builtin.get_variable_value('${authPass}'))
        elif data['authType'].lower() == 'digest':
            return HTTPDigestAuth(self.builtin.get_variable_value('${authUser}'),
                                  self.builtin.get_variable_value('${authPass}'))
        elif data['authType'].lower() == 'oauth1':
            from requests_oauthlib import OAuth1
            return OAuth1(self.builtin.get_variable_value('${oauth1_app_key}'),
                          self.builtin.get_variable_value('${oauth1_app_secret}'),
                          self.builtin.get_variable_value('${oauth1_user_token}'),
                          self.builtin.get_variable_value('${oauth1_user_token_secret}'))
        else:
            return None

    """ Setup Request Payload """

    @staticmethod
    def __set_payload(data):
        if data['reqPayload']:
            return data['reqPayload']
        return None

    """ Setup Request URL """

    def __set_url(self, data):
        url = (data['protocol'] or 'http').lower() + '://' + \
              self.builtin.get_variable_value('${host}', default='localhost')
        if data['port']:
            url += ':' + data['port']
        url += data['endPoint']
        return url

    """ Setup Headers """

    def __set_headers(self, data):
        return self.__get_dict(data['reqHeaders'])

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
        if self.http_proxy or self.https_proxy:
            return {
                'http': self.http_proxy,
                'https': self.https_proxy
            }
        else:
            return None

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
    def __get_dict(jsonData, default=None):
        if bool(jsonData):
            return json.loads(jsonData)
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
                validContents = self.__get_values_from_json_or_string(data=data,
                                                                      key='rspShouldContain',
                                                                      delimeter=',')
                for content in validContents:
                    if not content.strip() in response.text:
                        err.append('Response body does not contain expected: ' + content.strip())

            if data['rspShouldNotContain']:
                invalidContents = self.__get_values_from_json_or_string(data=data,
                                                                        key='rspShouldNotContain',
                                                                        delimeter=',')
                for content in invalidContents:
                    if content.strip() in response.text:
                        err.append('Response body contains unexpected: ' + content.strip())

        else:
            logger.info('Skipping Response Body Assertions')

    """ Validate Response Headers """

    def __assert_headers(self, response, data, err):
        expectedHeaders = self.__get_dict(data['rspHeadersShouldContain'], default={})
        unexpectedHeaders = self.__get_dict(data['rspHeadersShouldNotContain'], default={})

        if expectedHeaders or unexpectedHeaders:
            logger.info('Running Response Headers assertions..')
            if not all(header in response.headers.items() for header in expectedHeaders.items()):
                logger.error(pprint.pformat(response.headers)
                             + ' Does not contain one or more expected headers: '
                             + pprint.pformat(expectedHeaders))
                err.append('Response Headers missing expected value(s)')

            if any(header in response.headers.items() for header in unexpectedHeaders.items()):
                logger.error(pprint.pformat(response.headers)
                             + ' contains one or more unexpected headers: '
                             + pprint.pformat(unexpectedHeaders))
                err.append('Response Headers contains unexpected value(s)')
        else:
            logger.info('Skipping Response Headers Assertion')

    """ Validate Response SLA """

    @staticmethod
    def __assert_sla(response, data, err):
        if data['rspSLA']:
            rspSLA = float(data['rspSLA'])
            actualRspTime = response.elapsed.total_seconds() * 1000
            if rspSLA < actualRspTime:
                err.append(
                    'Expected Response SLA: ' + str(rspSLA) + '(ms) but actual was: ' + str(actualRspTime) + '(ms)')
            else:
                logger.info('Response SLA Validation Successful')
        else:
            logger.info("Response SLA not configured. Skipping validation.")

    """ Log Request """

    def __log_prepped_request(self, prepped, data, encoding=None):
        encoding = encoding or requests.utils.get_encoding_from_headers(prepped.headers)
        # logger.trace(encoding)
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
HTTP Proxy: {self.http_proxy}
HTTPS Proxy: {self.https_proxy}
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


class TLSAdapter(HTTPAdapter):
    """Transport adapter that forces use of TLSv1.2.
            All Tomcat Servers Require TLSv1.2 in DEV, QA, CTE or PROD environment."""

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        """Create and initialize the urllib3 PoolManager to use TLSv.12."""
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_version=ssl.PROTOCOL_TLSv1_2)


globals()[__name__] = QATLibrary
