# grafana_client.SsoSettingsApi

All URIs are relative to *http://localhost:3000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_provider_settings**](SsoSettingsApi.md#get_provider_settings) | **GET** /v1/sso-settings/{key} | Get an SSO Settings entry by Key
[**list_all_providers_settings**](SsoSettingsApi.md#list_all_providers_settings) | **GET** /v1/sso-settings | List all SSO Settings entries
[**remove_provider_settings**](SsoSettingsApi.md#remove_provider_settings) | **DELETE** /v1/sso-settings/{key} | Remove SSO Settings
[**update_provider_settings**](SsoSettingsApi.md#update_provider_settings) | **PUT** /v1/sso-settings/{key} | Update SSO Settings


# **get_provider_settings**
> ListAllProvidersSettings200ResponseInner get_provider_settings(key)

Get an SSO Settings entry by Key

You need to have a permission with action `settings:read` with scope `settings:auth.<provider>:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.list_all_providers_settings200_response_inner import ListAllProvidersSettings200ResponseInner
from grafana_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:3000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = grafana_client.Configuration(
    host = "http://localhost:3000/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_key
configuration.api_key['api_key'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# Configure HTTP basic authorization: basic
configuration = grafana_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with grafana_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = grafana_client.SsoSettingsApi(api_client)
    key = 'key_example' # str | 

    try:
        # Get an SSO Settings entry by Key
        api_response = api_instance.get_provider_settings(key)
        print("The response of SsoSettingsApi->get_provider_settings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SsoSettingsApi->get_provider_settings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**|  | 

### Return type

[**ListAllProvidersSettings200ResponseInner**](ListAllProvidersSettings200ResponseInner.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**401** | UnauthorizedError is returned when the request is not authenticated. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_all_providers_settings**
> List[ListAllProvidersSettings200ResponseInner] list_all_providers_settings()

List all SSO Settings entries

You need to have a permission with action `settings:read` with scope `settings:auth.<provider>:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.list_all_providers_settings200_response_inner import ListAllProvidersSettings200ResponseInner
from grafana_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:3000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = grafana_client.Configuration(
    host = "http://localhost:3000/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_key
configuration.api_key['api_key'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# Configure HTTP basic authorization: basic
configuration = grafana_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with grafana_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = grafana_client.SsoSettingsApi(api_client)

    try:
        # List all SSO Settings entries
        api_response = api_instance.list_all_providers_settings()
        print("The response of SsoSettingsApi->list_all_providers_settings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SsoSettingsApi->list_all_providers_settings: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[ListAllProvidersSettings200ResponseInner]**](ListAllProvidersSettings200ResponseInner.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**401** | UnauthorizedError is returned when the request is not authenticated. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_provider_settings**
> SuccessResponseBody remove_provider_settings(key)

Remove SSO Settings

Removes the SSO Settings for a provider.  You need to have a permission with action `settings:write` and scope `settings:auth.<provider>:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.success_response_body import SuccessResponseBody
from grafana_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:3000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = grafana_client.Configuration(
    host = "http://localhost:3000/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_key
configuration.api_key['api_key'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# Configure HTTP basic authorization: basic
configuration = grafana_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with grafana_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = grafana_client.SsoSettingsApi(api_client)
    key = 'key_example' # str | 

    try:
        # Remove SSO Settings
        api_response = api_instance.remove_provider_settings(key)
        print("The response of SsoSettingsApi->remove_provider_settings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SsoSettingsApi->remove_provider_settings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**|  | 

### Return type

[**SuccessResponseBody**](SuccessResponseBody.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | An OKResponse is returned if the request was successful. |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**401** | UnauthorizedError is returned when the request is not authenticated. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_provider_settings**
> SuccessResponseBody update_provider_settings(key, update_provider_settings_request)

Update SSO Settings

Inserts or updates the SSO Settings for a provider.  You need to have a permission with action `settings:write` and scope `settings:auth.<provider>:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.success_response_body import SuccessResponseBody
from grafana_client.models.update_provider_settings_request import UpdateProviderSettingsRequest
from grafana_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:3000/api
# See configuration.py for a list of all supported configuration parameters.
configuration = grafana_client.Configuration(
    host = "http://localhost:3000/api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: api_key
configuration.api_key['api_key'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['api_key'] = 'Bearer'

# Configure HTTP basic authorization: basic
configuration = grafana_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Enter a context with an instance of the API client
with grafana_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = grafana_client.SsoSettingsApi(api_client)
    key = 'key_example' # str | 
    update_provider_settings_request = grafana_client.UpdateProviderSettingsRequest() # UpdateProviderSettingsRequest | 

    try:
        # Update SSO Settings
        api_response = api_instance.update_provider_settings(key, update_provider_settings_request)
        print("The response of SsoSettingsApi->update_provider_settings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SsoSettingsApi->update_provider_settings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**|  | 
 **update_provider_settings_request** | [**UpdateProviderSettingsRequest**](UpdateProviderSettingsRequest.md)|  | 

### Return type

[**SuccessResponseBody**](SuccessResponseBody.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | An OKResponse is returned if the request was successful. |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**401** | UnauthorizedError is returned when the request is not authenticated. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

