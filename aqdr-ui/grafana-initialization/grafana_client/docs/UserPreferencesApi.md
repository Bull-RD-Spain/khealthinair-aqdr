# grafana_client.UserPreferencesApi

All URIs are relative to *http://localhost:3000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_user_preferences**](UserPreferencesApi.md#get_user_preferences) | **GET** /user/preferences | Get user preferences.
[**patch_user_preferences**](UserPreferencesApi.md#patch_user_preferences) | **PATCH** /user/preferences | Patch user preferences.
[**update_user_preferences**](UserPreferencesApi.md#update_user_preferences) | **PUT** /user/preferences | Update user preferences.


# **get_user_preferences**
> Preferences get_user_preferences()

Get user preferences.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.preferences import Preferences
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
    api_instance = grafana_client.UserPreferencesApi(api_client)

    try:
        # Get user preferences.
        api_response = api_instance.get_user_preferences()
        print("The response of UserPreferencesApi->get_user_preferences:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserPreferencesApi->get_user_preferences: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**Preferences**](Preferences.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**401** | UnauthorizedError is returned when the request is not authenticated. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_user_preferences**
> SuccessResponseBody patch_user_preferences(patch_prefs_cmd)

Patch user preferences.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.patch_prefs_cmd import PatchPrefsCmd
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
    api_instance = grafana_client.UserPreferencesApi(api_client)
    patch_prefs_cmd = grafana_client.PatchPrefsCmd() # PatchPrefsCmd | 

    try:
        # Patch user preferences.
        api_response = api_instance.patch_user_preferences(patch_prefs_cmd)
        print("The response of UserPreferencesApi->patch_user_preferences:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserPreferencesApi->patch_user_preferences: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patch_prefs_cmd** | [**PatchPrefsCmd**](PatchPrefsCmd.md)|  | 

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
**200** | An OKResponse is returned if the request was successful. |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**401** | UnauthorizedError is returned when the request is not authenticated. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_user_preferences**
> SuccessResponseBody update_user_preferences(update_prefs_cmd)

Update user preferences.

Omitting a key (`theme`, `homeDashboardId`, `timezone`) will cause the current value to be replaced with the system default value.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.success_response_body import SuccessResponseBody
from grafana_client.models.update_prefs_cmd import UpdatePrefsCmd
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
    api_instance = grafana_client.UserPreferencesApi(api_client)
    update_prefs_cmd = grafana_client.UpdatePrefsCmd() # UpdatePrefsCmd | 

    try:
        # Update user preferences.
        api_response = api_instance.update_user_preferences(update_prefs_cmd)
        print("The response of UserPreferencesApi->update_user_preferences:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserPreferencesApi->update_user_preferences: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **update_prefs_cmd** | [**UpdatePrefsCmd**](UpdatePrefsCmd.md)|  | 

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
**200** | An OKResponse is returned if the request was successful. |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**401** | UnauthorizedError is returned when the request is not authenticated. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

