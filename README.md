# QATLibrary 
![gh ci](https://github.com/sharif314/QATLibrary/workflows/QATLibrary%20CI/badge.svg)
![gh tests](https://github.com/sharif314/QATLibrary/workflows/Test/badge.svg)
[![PyPI version](https://badge.fury.io/py/QATLibrary.svg)](https://badge.fury.io/py/QATLibrary)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-blue.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)


QAT (Quick API Tests) Library is a Data/Configuration Driven REST API Test Automation Library. 
Can be used as a Robot Framework Library or as standalone tool (CLI). This tool does not solve complex 
REST API automation scenarios, rather, provides a simple, lightweight and data-driven approach to create 
automated REST API tests quickly. For complex flows, it is recommended to use the library with Robot 
Framework. 

## Features
* No coding required. Quick and easy implementation for REST API Tests. 
* Initialize sample config and Test Data with a single command. 
* Run from CLI (CI/CD friendly).
* Store Test Data, Documentation and Assertions in CSV File. 
* Authorization: Basic, Digest, OAuth1
* Run as a Robot Framework Library with Dynamic Test Generation Support. 
* Supports all HTTP Methods, SSL Certificates, Proxy Server, Stream, Redirection, Request Timeout etc.
* Robot Framework based execution, reports and logs (CLI or Library). 

### Built-in Assertions
* Status Code
* JSON Schema
* Response Body 
* Response Headers
* Response Time/SLA
* Server Certificate

## Install QATLibrary
``QATLibrary`` is available in [PyPI](https://pypi.org/project/QATLibrary/). You can install using [Pip](https://pip.pypa.io/en/stable/):
```shell 
pip install qatlibrary
```

## Execution 
#### Getting started from scratch is only a few commands away. Follow - 
1. Generate Sample Test Data CSV and Config YAML from CLI run _(Skip this step if you already have Test Data and Config files)_:
    ```shell 
    qat init
    ```
2. Execute Tests Using CLI _(standalone)_:
    ```shell
    qat run -c config.yaml -f TestCases.csv
    ```
3. Delete report files (*.html and *.xml) in current directory:
    ```shell
    qat clean
    ```
    or to clean a specific report directory:
    ```shell
    qat clean -d path/to/dir
    ```

4. For CLI Help (shows all required and optional args, usage etc):
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
configurations during execution. 

Generating Sample Test Data CSV and Config YAML is easy. Simply run:

```shell 
qat init
```

This command should generate two sample files like below - 
1. [Sample CSV Test Data](https://github.com/sharif314/QATLibrary/blob/main/sample/TestCases.csv): Test Cases or Data file. 
Test cases gets generated based on this file's content using Robot Framework. 

2. [Sample Config YAML](https://github.com/sharif314/QATLibrary/blob/main/sample/config.yaml): This file contains various runtime configurations 
for tests. Can be utilize to accommodate various CI or Test environments. Please follow the inline comments for more details -  
    ```yaml
    ---
    # optional args; uncomment as-needed. 
    # Any block or k/v not required, recommended to keep commented out for reasonable defaults. 
    base_url: httpbin.org           # base url/server name. Default localhost
    timeout: 10                     # In seconds. Default 5 seconds
    allow_redirects: True           # Allow Redirects. Default True.
    stream: False                   # True/False. Default False.
    
    ## global headers - these are added to every request from your data csv. All headers should be strings.
    headers:
      user-agent: QATLibrary                                  # this is a static header
      Authorization: Basic c29tZXVzZXI6bm90dmVyeXNlY3JldHBhc3M=
      # dynamic headers can be added with ${{ }} syntax like below -
      X-correlation-id: ${{str(__import__('uuid').uuid4())}}         # dynamic headers use python's eval func.
      random-digit: ${{str(__import__('random').randint(0,99))}}     # dynamic headers use python's eval func.
    
    
    ## To enable proxies for http/https, enable the following config.
    #proxies:
    #  http_proxy:                   # HTTP proxy. Default None.
    #  https_proxy:                  # HTTPS proxy. Default None.
    #  no_proxy:                     # Bypass proxy
    
    ## SSL/TLS configuration for REST API calls. Enable to configure.
    #tls:
    #  verify_server_cert: True      # True/False or path to CA Bundle. Default False.
    #  certificate:                  # .pem format certificate. Default None
    #  private_key:                  # .pem format private key (unencrypted). Default None.
    
    ## Note that the specific details of how to obtain an access token may vary depending on the authentication scheme and API provider.
    ## Be sure to check the API documentation for instructions on how to obtain an access token for your use case.
    ## bearer auth / access token config. Enable below configs if required.
    
    #bearer_auth:
    #  token_url:                                # token_url for bearer auth
    #  payload:                                  # generic payload. supports all direct key/value. below are the common ones.
    #    client_id:
    #    client_secret:
    #    scope:
    #    grant_type:
    
    ## Enable following block for bearer auth TLS config.
    #  tls:
    #    verify_server_cert: True       # True/False or path to CA Bundle. Default False.
    #    certificate:                  # .pem format certificate. Default None
    #    private_key:                  # .pem format private key (unencrypted). Default None

   ```

Once the files are generated, you can rename them according to your test suites or requirements.  

## Contributing
This is [Sharif](https://www.linkedin.com/in/sharif-rahman/). I started this project basically to make my life 
a bit easier around simple REST API tests. This project is ideal for you if want to get some automated tests done 
quickly for your projects without coding and powerful assertion methods out of the box. 

QATLibrary is on [GitHub](https://github.com/toil-free/QATLibrary.git). 
Get in touch, via GitHub or otherwise, if you've got something to contribute, it'd be most welcome! 
Please follow the [CONTRIBUTING.md]( https://github.com/toil-free/QATLibrary/blob/main/CONTRIBUTING.md) for detailed guidelines.

## License 
QATLibrary is open source software provided under the MIT License. Please follow [LICENSE.md]( https://github.com/toil-free/QATLibrary/blob/main/LICENSE.md) for more details. 
