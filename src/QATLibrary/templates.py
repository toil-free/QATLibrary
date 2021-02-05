CONFIG_FILE_CONTENT = '''
---
#optional args
host: httpbin.org           # Default localhost

timeout: 10                 # Default 5 seconds
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
'''

CSV_DATA_FILE_CONTENT = '''testName,execute,testId,testOwner,tags,documentation,protocol,port,endPoint,reqType,authType,reqHeaders,reqCookies,reqFiles,reqParams,reqPayload,statusCode,rspSLA,jsonSchema,rspShouldContain,rspShouldNotContain,rspHeadersShouldContain,rspHeadersShouldNotContain
GET Request without Headers,Y,JIRA-11,Jane Doe,"SMOKE, COHERENCE","Here goes my Test Documentation. E.g Expected result ""x"" should be equal to actual result ""y"". ",Https,,/get,GET,,,,,,,200,,,"""Host"": ""httpbin.org""","wrong, Failed, error, Error",,"{
	""invalidHeader"": ""unexpected""
}"
GET Request without Headers and Protocol,Y,JIRA-11,Jane Doe,"SMOKE, COHERENCE","Here goes my Test Documentation. E.g Expected result ""x"" should be equal to actual result ""y"". ",,,/get,GET,,,,,,,200,,,"""Host"": ""httpbin.org""","wrong, Failed, error, Error",,"{
	""invalidHeader"": ""unexpected""
}"
GET Request with Custom Headers,Y,JIRA-21,Jane Doe,"SMOKE, COHERENCE","Here goes my Test Documentation. E.g Expected result ""x"" should be equal to actual result ""y"". ",Https,,/get,GET,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}",,,,,200,,,"""Host"": ""httpbin.org""","{""values"": [""unexpectedString"", ""wrong""]}","{
	""content-type"": ""application/json"",
	""Connection"": ""keep-alive""
}","{
	""invalidHeader"": ""unexpected""
}"
GET Request with Query Params,Y,JIRA-22,Jane Doe,"SMOKE, REGRESSION","Here goes my Test Documentation. E.g Expected result ""x"" should be equal to actual result ""y"". ",Https,,/get,GET,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br"", 
	  ""Cookie"": ""cookie1=value1; cookie2=value2""
}",,,,,200,,,"""Host"": ""httpbin.org""","{""values"": [""unexpectedString"", ""wrong""]}","{
	""content-type"": ""application/json"",
	""Connection"": ""keep-alive""
}","{
	""invalidHeader"": ""unexpected""
}"
GET Request with Cookies,Y,JIRA-26,Jane Doe,"SMOKE, REGRESSION","Here goes my Test Documentation. E.g Expected result ""x"" should be equal to actual result ""y"". ",Https,,/get,GET,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}","{
	""cookie1"": ""value1"",
	""cookie2"": ""value2""
}",,"{
	""key1"": ""value1"",
	""ke2"": ""value2""
}",,200,1000,,"""Host"": ""httpbin.org""","{""values"": [""unexpectedString"", ""wrong""]}","{
	""content-type"": ""application/json"",
	""Connection"": ""keep-alive""
}","{
	""invalidHeader"": ""unexpected""
}"
POST Request with JSON,Y,JIRA-12,John Doe,,My POST HTTP Request Should Succeed,https,443,/post,POST,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}",,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}","{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}",200,1000,,"{ ""values"": [""httpbin.org"", ""content-type""] }","Error, Failed","{
	""content-type"": ""application/json"",
	""Connection"": ""keep-alive""
}",
POST Request with XML Body,Y,JIRA-13,Jane Doe,,My Test Case Should Run,https,443,/post,POST,,"{
	""content-type"": ""application/xml"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}",,,,"<?xml version=""1.0"" encoding=""UTF-8""?>
<root>
   <Accept>application/json</Accept>
   <Accept-Encoding>gzip, deflate, br</Accept-Encoding>
   <Connection>keep-alive</Connection>
   <content-type>application/json;charset=UTF-8</content-type>
</root>",200,1000,,,"Error, Failed",,
PUT Request Should Fail with 405 Error,Y,JIRA-14,Jane Doe,,HTTPBin should return 405,https,443,/post,PUT,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}",,,,,405,1000,,Method Not Allowed,Success,,
DELETE Request without Request Body,Y,JIRA-112,John Doe,,My Test Case Should Run,https,443,/delete,DELETE,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}",,,,,200,1000,,"""json"": null, ""form"": {}","Error, Failed",,
DELETE Request with Request Body,Y,JIRA-114,John Doe,,My Test Case Should Run,https,443,/delete,DELETE,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}",,,,"{
	""content-type"": ""application/json;charset=UTF-8"",
	""Connection"": ""keep-alive"",
	""Accept"": ""application/json"",
	""Accept-Encoding"": ""gzip, deflate, br""
}",200,1000,"{
    ""$schema"": ""http://json-schema.org/draft-07/schema"",
    ""$id"": ""http://example.com/example.json"",
    ""type"": ""object"",
    ""title"": ""The root schema"",
    ""description"": ""The root schema comprises the entire JSON document."",
    ""default"": {},
    ""examples"": [
        {
            ""args"": {},
            ""headers"": {
                ""Accept"": ""application/json"",
                ""Accept-Encoding"": ""gzip, deflate, br"",
                ""Content-Type"": ""application/json;charset=UTF-8"",
                ""Host"": ""httpbin.org"",
                ""User-Agent"": ""python-requests/2.25.1"",
                ""X-Amzn-Trace-Id"": ""Root=1-600d22e1-1a20acc71dc248c55d2d5e59""
            },
            ""origin"": ""75.22.161.77"",
            ""url"": ""https://httpbin.org/get""
        }
    ],
    ""required"": [
        ""args"",
        ""headers"",
        ""origin"",
        ""url""
    ],
    ""properties"": {
        ""args"": {
            ""$id"": ""#/properties/args"",
            ""type"": ""object"",
            ""title"": ""The args schema"",
            ""description"": ""An explanation about the purpose of this instance."",
            ""default"": {},
            ""examples"": [
                {}
            ],
            ""required"": [],
            ""additionalProperties"": true
        },
        ""headers"": {
            ""$id"": ""#/properties/headers"",
            ""type"": ""object"",
            ""title"": ""The headers schema"",
            ""description"": ""An explanation about the purpose of this instance."",
            ""default"": {},
            ""examples"": [
                {
                    ""Accept"": ""application/json"",
                    ""Accept-Encoding"": ""gzip, deflate, br"",
                    ""Content-Type"": ""application/json;charset=UTF-8"",
                    ""Host"": ""httpbin.org"",
                    ""User-Agent"": ""python-requests/2.25.1"",
                    ""X-Amzn-Trace-Id"": ""Root=1-600d22e1-1a20acc71dc248c55d2d5e59""
                }
            ],
            ""required"": [
                ""Accept"",
                ""Accept-Encoding"",
               ""Host"",
                ""User-Agent"",
                ""X-Amzn-Trace-Id""
            ],
            ""properties"": {
                ""Accept"": {
                    ""$id"": ""#/properties/headers/properties/Accept"",
                    ""type"": ""string"",
                    ""title"": ""The Accept schema"",
                    ""description"": ""An explanation about the purpose of this instance."",
                    ""default"": """",
                    ""examples"": [
                        ""application/json""
                    ]
                },
                ""Accept-Encoding"": {
                    ""$id"": ""#/properties/headers/properties/Accept-Encoding"",
                    ""type"": ""string"",
                    ""title"": ""The Accept-Encoding schema"",
                    ""description"": ""An explanation about the purpose of this instance."",
                    ""default"": """",
                    ""examples"": [
                        ""gzip, deflate, br""
                    ]
                },
                ""Content-Type"": {
                    ""$id"": ""#/properties/headers/properties/Content-Type"",
                    ""type"": ""string"",
                    ""title"": ""The Content-Type schema"",
                    ""description"": ""An explanation about the purpose of this instance."",
                    ""default"": """",
                    ""examples"": [
                        ""application/json;charset=UTF-8""
                    ]
                },
                ""Host"": {
                    ""$id"": ""#/properties/headers/properties/Host"",
                    ""type"": ""string"",
                    ""title"": ""The Host schema"",
                    ""description"": ""An explanation about the purpose of this instance."",
                    ""default"": """",
                    ""examples"": [
                        ""httpbin.org""
                    ]
                },
                ""User-Agent"": {
                    ""$id"": ""#/properties/headers/properties/User-Agent"",
                    ""type"": ""string"",
                    ""title"": ""The User-Agent schema"",
                    ""description"": ""An explanation about the purpose of this instance."",
                    ""default"": """",
                    ""examples"": [
                        ""python-requests/2.25.1""
                    ]
                },
                ""X-Amzn-Trace-Id"": {
                    ""$id"": ""#/properties/headers/properties/X-Amzn-Trace-Id"",
                    ""type"": ""string"",
                    ""title"": ""The X-Amzn-Trace-Id schema"",
                    ""description"": ""An explanation about the purpose of this instance."",
                    ""default"": """",
                    ""examples"": [
                        ""Root=1-600d22e1-1a20acc71dc248c55d2d5e59""
                    ]
                }
            },
            ""additionalProperties"": true
        },
        ""origin"": {
            ""$id"": ""#/properties/origin"",
            ""type"": ""string"",
            ""title"": ""The origin schema"",
            ""description"": ""An explanation about the purpose of this instance."",
            ""default"": """",
            ""examples"": [
                ""75.22.161.77""
            ]
        },
        ""url"": {
            ""$id"": ""#/properties/url"",
            ""type"": ""string"",
            ""title"": ""The url schema"",
            ""description"": ""An explanation about the purpose of this instance."",
            ""default"": """",
            ""examples"": [
                ""https://httpbin.org/get""
            ]
        }
    },
    ""additionalProperties"": true
}","""form"": {}","Error, Failed",,
'''