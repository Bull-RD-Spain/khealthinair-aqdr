# grafana_client.OrgInvitesApi

All URIs are relative to *http://localhost:3000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_org_invite**](OrgInvitesApi.md#add_org_invite) | **POST** /org/invites | Add invite.
[**get_pending_org_invites**](OrgInvitesApi.md#get_pending_org_invites) | **GET** /org/invites | Get pending invites.
[**revoke_invite**](OrgInvitesApi.md#revoke_invite) | **DELETE** /org/invites/{invitation_code}/revoke | Revoke invite.


# **add_org_invite**
> SuccessResponseBody add_org_invite(add_invite_form)

Add invite.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.add_invite_form import AddInviteForm
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
    api_instance = grafana_client.OrgInvitesApi(api_client)
    add_invite_form = grafana_client.AddInviteForm() # AddInviteForm | 

    try:
        # Add invite.
        api_response = api_instance.add_org_invite(add_invite_form)
        print("The response of OrgInvitesApi->add_org_invite:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrgInvitesApi->add_org_invite: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **add_invite_form** | [**AddInviteForm**](AddInviteForm.md)|  | 

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**412** | (empty) |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_pending_org_invites**
> List[TempUserDTO] get_pending_org_invites()

Get pending invites.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.temp_user_dto import TempUserDTO
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
    api_instance = grafana_client.OrgInvitesApi(api_client)

    try:
        # Get pending invites.
        api_response = api_instance.get_pending_org_invites()
        print("The response of OrgInvitesApi->get_pending_org_invites:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrgInvitesApi->get_pending_org_invites: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[TempUserDTO]**](TempUserDTO.md)

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_invite**
> SuccessResponseBody revoke_invite(invitation_code)

Revoke invite.

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
    api_instance = grafana_client.OrgInvitesApi(api_client)
    invitation_code = 'invitation_code_example' # str | 

    try:
        # Revoke invite.
        api_response = api_instance.revoke_invite(invitation_code)
        print("The response of OrgInvitesApi->revoke_invite:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrgInvitesApi->revoke_invite: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invitation_code** | **str**|  | 

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
**200** | An OKResponse is returned if the request was successful. |  -  |
**401** | UnauthorizedError is returned when the request is not authenticated. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

