# QATLibrary 
QAT (Quick API Tests) Library is a Data/Configuration Driven REST API Test Automation Library. 
Can be used as a Robot Framework Library or as standalone tool (CLI). This tool does not solve complex 
REST API automation scenarios, however, provides a quick, lightweight and data-driven approach to validate 
REST API tests. If you need complex flows for your tests, please use the library with Robot Framework where 
custom keywords can be used with (dynamically) generated tests by QATLibrary.

## Getting Started
### Pre-reqs:
* Python >= 3.6

### Install QATLibrary
Using Pip:
```shell 
pip install qatlibrary
```
From source:
```shell 
python setup.py install
```

## Execution
Using CLI (standalone)
```shell
qat -c config.yaml -f Tests.csv 
```

CLI Help
```shell
qat --help
```

## As Robot Framework Library
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
* [Sample Config Yaml](sample/config.yaml): Required to inject runtime configurations
```yaml
host: httpbin.org 

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
* [CSV Test Data](sample/Tests.csv): Test cases/data file. Test cases gets generated based on this file's data


## Contributing
This is [Sharif Rahman](https://www.linkedin.com/in/sharif-rahman/). 

QATLibrary is on [GitHub](https://github.com/sharif314/QATLibrary). 
Get in touch, via GitHub or otherwise, if you've got something to contribute, it'd be most welcome! 
Please follow the [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License 
QATLibrary is open source software provided under the MIT License. Please follow [LICENSE.md](LICENSE.md) for more details. 
