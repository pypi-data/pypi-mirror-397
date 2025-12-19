# cloudmersive_spam_api_client
Easily and directly scan and block spam security threats in input.

This Python package provides a native API client for [Cloudmersive Spam Detection API](https://cloudmersive.com/spam-detection-api)

- API version: v1
- Package version: 3.0.4
- Build package: io.swagger.codegen.languages.PythonClientCodegen

## Requirements.

Python 2.7 and 3.4+

## Installation & Usage
### pip install

If the python package is hosted on Github, you can install directly from Github

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import cloudmersive_spam_api_client 
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import cloudmersive_spam_api_client
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python
from __future__ import print_function
import time
import cloudmersive_spam_api_client
from cloudmersive_spam_api_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: Apikey
configuration = cloudmersive_spam_api_client.Configuration()
configuration.api_key['Apikey'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Apikey'] = 'Bearer'

# create an instance of the API class
api_instance = cloudmersive_spam_api_client.SpamDetectionApi(cloudmersive_spam_api_client.ApiClient(configuration))
model = 'Advanced' # str | Optional: Specify which AI model to use.  Possible choices are Normal and Advanced.  Default is Advanced. (optional) (default to Advanced)
preprocessing = 'Auto' # str | Optional: Specify which preprocessing to Use.  Possible choices are None, Compatability and Auto.  Default is Auto. (optional) (default to Auto)
allow_phishing = false # bool | True if phishing should be allowed, false otherwise (optional) (default to false)
allow_unsolicited_sales = false # bool | True if unsolicited sales should be allowed, false otherwise (optional) (default to false)
allow_promotional_content = true # bool | True if promotional content should be allowed, false otherwise (optional) (default to true)
custom_policy_id = 'custom_policy_id_example' # str | Apply a Custom Policy for Spam Enforcement by providing the ID; to create a Custom Policy, navigate to the Cloudmersive Management Portal and select Custom Policies.  Requires Managed Instance or Private Cloud (optional)
input_file = '/path/to/file.txt' # file |  (optional)

try:
    # Perform advanced AI spam detection and classification against input text file.
    api_response = api_instance.spam_detect_file_advanced_post(model=model, preprocessing=preprocessing, allow_phishing=allow_phishing, allow_unsolicited_sales=allow_unsolicited_sales, allow_promotional_content=allow_promotional_content, custom_policy_id=custom_policy_id, input_file=input_file)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SpamDetectionApi->spam_detect_file_advanced_post: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*SpamDetectionApi* | [**spam_detect_file_advanced_post**](docs/SpamDetectionApi.md#spam_detect_file_advanced_post) | **POST** /spam/detect/file/advanced | Perform advanced AI spam detection and classification against input text file.
*SpamDetectionApi* | [**spam_detect_file_post**](docs/SpamDetectionApi.md#spam_detect_file_post) | **POST** /spam/detect/file | Perform AI spam detection and classification on an input image or document (PDF or DOCX)
*SpamDetectionApi* | [**spam_detect_form_submission_advanced_post**](docs/SpamDetectionApi.md#spam_detect_form_submission_advanced_post) | **POST** /spam/detect/form-submission/advanced | Perform advanced AI spam detection and classification against a form submission
*SpamDetectionApi* | [**spam_detect_text_string_advanced_post**](docs/SpamDetectionApi.md#spam_detect_text_string_advanced_post) | **POST** /spam/detect/text-string/advanced | Perform advanced AI spam detection and classification against input text string
*SpamDetectionApi* | [**spam_detect_text_string_post**](docs/SpamDetectionApi.md#spam_detect_text_string_post) | **POST** /spam/detect/text-string | Perform AI spam detection and classification against input text string


## Documentation For Models

 - [SpamDetectionAdvancedFormField](docs/SpamDetectionAdvancedFormField.md)
 - [SpamDetectionAdvancedFormSubmissionRequest](docs/SpamDetectionAdvancedFormSubmissionRequest.md)
 - [SpamDetectionAdvancedRequest](docs/SpamDetectionAdvancedRequest.md)
 - [SpamDetectionAdvancedResponse](docs/SpamDetectionAdvancedResponse.md)
 - [SpamDetectionFormSubmissionAdvancedResponse](docs/SpamDetectionFormSubmissionAdvancedResponse.md)
 - [SpamDetectionRequest](docs/SpamDetectionRequest.md)
 - [SpamDetectionResponse](docs/SpamDetectionResponse.md)


## Documentation For Authorization


## Apikey

- **Type**: API key
- **API key parameter name**: Apikey
- **Location**: HTTP header


## Author



