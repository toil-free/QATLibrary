# QATLibrary 
QAT (Quick API Tests) Library is a Data/Configuration Driven REST API Test Automation Library. 
Can be used as a Robot Framework Library or as standalone tool (CLI). This tool does not solve complex 
REST API automation scenarios, rather, provides a simple, lightweight and data-driven approach to create 
automated REST API tests quickly. For complex flows, it is recommended to use the library with Robot 
Framework. 

## Features
* No coding required. Quick and easy implementation for REST API Tests. 
* Run from CLI (CI/CD friendly).
* Store Test Data, Documentation and Assertions in CSV File. 
* Authorization: Basic, Digest, OAuth1
* Run as a Robot Framework Library with Dynamic Test Generation Support. 
* Supports all HTTP Methods, SSL Certificates, Proxy Server, Stream, Redirection, Request Timeout etc.
* Robot Framework based execution, reports and logs (CLI or Library). 

### Assertions
* Status Code
* JSON Schema
* Response Body 
* Response Headers
* Response Time/SLA
* Server Certificate


## Install QATLibrary
Using Pip:
```shell 
pip install qatlibrary
```
From Source:
```shell 
python setup.py install
```

## Execution
Using CLI (standalone):
```shell
qat -c sample/config.yaml -f sample/Tests.csv 
```

CLI Help:
```shell
qat --help
```

## Use as Robot Framework Library
Example:

```robot
*** Settings ***
Library          QATLibrary
Suite Setup      QAT Dynamic Tests Setup        csvFile=${csvData}
Variables        config.yaml        # Or can be a robot framework variable (Test/Suite/Variablefile etc.)

*** Variables ***
${host}          httpbin.org
${csvData}       Tests.csv

*** Test Cases ***
Place Holder Test
    [Documentation]  Placeholder Test Required by Robot Framework Suite Runner.  
    No Operaiton 

```

## Configurations and Test Data
QATLibrary requires a CSV file with required data to drive the tests. Config yaml or .py files can inject your desired
configurations during runtime.
* [CSV Test Data](https://github.com/sharif314/QATLibrary/blob/main/sample/Tests.csv): Test cases/data file. Test cases gets generated based on this file's data 
using Robot Framework. 

* [Sample Config YAML](https://github.com/sharif314/QATLibrary/blob/main/sample/config.yaml): Required to inject runtime configurations
```yaml
host: httpbin.org           # Required

#optional args
timeout: 5                  # Default 5 seconds
allow_redirects:            # Allow Redirects. Default True. 
stream:                     # True/False. 
http_proxy:                 # HTTP Proxy. Default None. 
https_proxy:                # HTTPS Proxy. Default None.

verify_server_cert: True    # True/False or path to CA Bundle. Default False. 
certificate:                # .pem format certificate. Default None
private_key:                # .pem format private key (unencrypted). Default None

# Required if using Basic/Digest Auth (Default None)
authUser:             
authPass:

# Required if using OAuth1 auth (Default None)
oauth1_app_key:
oauth1_app_secret:
oauth1_user_token:
oauth1_user_token_secret:
```



## Contributing
This is [Sharif](https://www.linkedin.com/in/sharif-rahman/). I started this project basically to make my life 
a bit easier around simple REST API tests. This project is ideal for you if want to get some automated tests done 
quickly for your projects without coding and powerful assertion methods out of the box. 

QATLibrary is on [GitHub](https://github.com/sharif314/QATLibrary). 
Get in touch, via GitHub or otherwise, if you've got something to contribute, it'd be most welcome! 
Please follow the [CONTRIBUTING.md](https://github.com/sharif314/QATLibrary/blob/main/CONTRIBUTING.md) for detailed guidelines.

## License 
QATLibrary is open source software provided under the MIT License. Please follow [LICENSE.md](https://github.com/sharif314/QATLibrary/blob/main/LICENSE.md) for more details. 
