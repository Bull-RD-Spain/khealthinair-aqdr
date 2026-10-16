# grafana_client.AccessControlApi

All URIs are relative to *http://localhost:3000/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_team_role**](AccessControlApi.md#add_team_role) | **POST** /access-control/teams/{teamId}/roles | Add team role.
[**add_user_role**](AccessControlApi.md#add_user_role) | **POST** /access-control/users/{userId}/roles | Add a user role assignment.
[**create_role**](AccessControlApi.md#create_role) | **POST** /access-control/roles | Create a new custom role.
[**delete_role**](AccessControlApi.md#delete_role) | **DELETE** /access-control/roles/{roleUID} | Delete a custom role.
[**get_access_control_status**](AccessControlApi.md#get_access_control_status) | **GET** /access-control/status | Get status.
[**get_resource_description**](AccessControlApi.md#get_resource_description) | **GET** /access-control/{resource}/description | Get a description of a resource&#39;s access control properties.
[**get_resource_permissions**](AccessControlApi.md#get_resource_permissions) | **GET** /access-control/{resource}/{resourceID} | Get permissions for a resource.
[**get_role**](AccessControlApi.md#get_role) | **GET** /access-control/roles/{roleUID} | Get a role.
[**get_role_assignments**](AccessControlApi.md#get_role_assignments) | **GET** /access-control/roles/{roleUID}/assignments | Get role assignments.
[**list_roles**](AccessControlApi.md#list_roles) | **GET** /access-control/roles | Get all roles.
[**list_team_roles**](AccessControlApi.md#list_team_roles) | **GET** /access-control/teams/{teamId}/roles | Get team roles.
[**list_teams_roles**](AccessControlApi.md#list_teams_roles) | **POST** /access-control/teams/roles/search | List roles assigned to multiple teams.
[**list_user_roles**](AccessControlApi.md#list_user_roles) | **GET** /access-control/users/{userId}/roles | List roles assigned to a user.
[**list_users_roles**](AccessControlApi.md#list_users_roles) | **POST** /access-control/users/roles/search | List roles assigned to multiple users.
[**remove_team_role**](AccessControlApi.md#remove_team_role) | **DELETE** /access-control/teams/{teamId}/roles/{roleUID} | Remove team role.
[**remove_user_role**](AccessControlApi.md#remove_user_role) | **DELETE** /access-control/users/{userId}/roles/{roleUID} | Remove a user role assignment.
[**set_resource_permissions**](AccessControlApi.md#set_resource_permissions) | **POST** /access-control/{resource}/{resourceID} | Set resource permissions.
[**set_resource_permissions_for_built_in_role**](AccessControlApi.md#set_resource_permissions_for_built_in_role) | **POST** /access-control/{resource}/{resourceID}/builtInRoles/{builtInRole} | Set resource permissions for a built-in role.
[**set_resource_permissions_for_team**](AccessControlApi.md#set_resource_permissions_for_team) | **POST** /access-control/{resource}/{resourceID}/teams/{teamID} | Set resource permissions for a team.
[**set_resource_permissions_for_user**](AccessControlApi.md#set_resource_permissions_for_user) | **POST** /access-control/{resource}/{resourceID}/users/{userID} | Set resource permissions for a user.
[**set_role_assignments**](AccessControlApi.md#set_role_assignments) | **PUT** /access-control/roles/{roleUID}/assignments | Set role assignments.
[**set_team_roles**](AccessControlApi.md#set_team_roles) | **PUT** /access-control/teams/{teamId}/roles | Update team role.
[**set_user_roles**](AccessControlApi.md#set_user_roles) | **PUT** /access-control/users/{userId}/roles | Set user role assignments.
[**update_role**](AccessControlApi.md#update_role) | **PUT** /access-control/roles/{roleUID} | Update a custom role.


# **add_team_role**
> SuccessResponseBody add_team_role(team_id, add_team_role_command)

Add team role.

You need to have a permission with action `teams.roles:add` and scope `permissions:type:delegate`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.add_team_role_command import AddTeamRoleCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    team_id = 56 # int | 
    add_team_role_command = grafana_client.AddTeamRoleCommand() # AddTeamRoleCommand | 

    try:
        # Add team role.
        api_response = api_instance.add_team_role(team_id, add_team_role_command)
        print("The response of AccessControlApi->add_team_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->add_team_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **team_id** | **int**|  | 
 **add_team_role_command** | [**AddTeamRoleCommand**](AddTeamRoleCommand.md)|  | 

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_user_role**
> SuccessResponseBody add_user_role(user_id, add_user_role_command)

Add a user role assignment.

Assign a role to a specific user. For bulk updates consider Set user role assignments.  You need to have a permission with action `users.roles:add` and scope `permissions:type:delegate`. `permissions:type:delegate` scope ensures that users can only assign roles which have same, or a subset of permissions which the user has. For example, if a user does not have required permissions for creating users, they won’t be able to assign a role which will allow to do that. This is done to prevent escalation of privileges.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.add_user_role_command import AddUserRoleCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    user_id = 56 # int | 
    add_user_role_command = grafana_client.AddUserRoleCommand() # AddUserRoleCommand | 

    try:
        # Add a user role assignment.
        api_response = api_instance.add_user_role(user_id, add_user_role_command)
        print("The response of AccessControlApi->add_user_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->add_user_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **int**|  | 
 **add_user_role_command** | [**AddUserRoleCommand**](AddUserRoleCommand.md)|  | 

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_role**
> RoleDTO create_role(create_role_form)

Create a new custom role.

Creates a new custom role and maps given permissions to that role. Note that roles with the same prefix as Fixed Roles can’t be created.  You need to have a permission with action `roles:write` and scope `permissions:type:delegate`. `permissions:type:delegate` scope ensures that users can only create custom roles with the same, or a subset of permissions which the user has. For example, if a user does not have required permissions for creating users, they won’t be able to create a custom role which allows to do that. This is done to prevent escalation of privileges.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.create_role_form import CreateRoleForm
from grafana_client.models.role_dto import RoleDTO
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
    api_instance = grafana_client.AccessControlApi(api_client)
    create_role_form = grafana_client.CreateRoleForm() # CreateRoleForm | 

    try:
        # Create a new custom role.
        api_response = api_instance.create_role(create_role_form)
        print("The response of AccessControlApi->create_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->create_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_role_form** | [**CreateRoleForm**](CreateRoleForm.md)|  | 

### Return type

[**RoleDTO**](RoleDTO.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | (empty) |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_role**
> SuccessResponseBody delete_role(role_uid, force=force, var_global=var_global)

Delete a custom role.

Delete a role with the given UID, and it’s permissions. If the role is assigned to a built-in role, the deletion operation will fail, unless force query param is set to true, and in that case all assignments will also be deleted.  You need to have a permission with action `roles:delete` and scope `permissions:type:delegate`. `permissions:type:delegate` scope ensures that users can only delete a custom role with the same, or a subset of permissions which the user has. For example, if a user does not have required permissions for creating users, they won’t be able to delete a custom role which allows to do that.

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
    api_instance = grafana_client.AccessControlApi(api_client)
    role_uid = 'role_uid_example' # str | 
    force = True # bool |  (optional)
    var_global = True # bool |  (optional)

    try:
        # Delete a custom role.
        api_response = api_instance.delete_role(role_uid, force=force, var_global=var_global)
        print("The response of AccessControlApi->delete_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->delete_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_uid** | **str**|  | 
 **force** | **bool**|  | [optional] 
 **var_global** | **bool**|  | [optional] 

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
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_access_control_status**
> int get_access_control_status()

Get status.

Returns an indicator to check if fine-grained access control is enabled or not.  You need to have a permission with action `status:accesscontrol` and scope `services:accesscontrol`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
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
    api_instance = grafana_client.AccessControlApi(api_client)

    try:
        # Get status.
        api_response = api_instance.get_access_control_status()
        print("The response of AccessControlApi->get_access_control_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->get_access_control_status: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**int**

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_resource_description**
> Description get_resource_description(resource)

Get a description of a resource's access control properties.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.description import Description
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
    api_instance = grafana_client.AccessControlApi(api_client)
    resource = 'resource_example' # str | 

    try:
        # Get a description of a resource's access control properties.
        api_response = api_instance.get_resource_description(resource)
        print("The response of AccessControlApi->get_resource_description:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->get_resource_description: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 

### Return type

[**Description**](Description.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_resource_permissions**
> List[ResourcePermissionDTO] get_resource_permissions(resource, resource_id)

Get permissions for a resource.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.resource_permission_dto import ResourcePermissionDTO
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
    api_instance = grafana_client.AccessControlApi(api_client)
    resource = 'resource_example' # str | 
    resource_id = 'resource_id_example' # str | 

    try:
        # Get permissions for a resource.
        api_response = api_instance.get_resource_permissions(resource, resource_id)
        print("The response of AccessControlApi->get_resource_permissions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->get_resource_permissions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **resource_id** | **str**|  | 

### Return type

[**List[ResourcePermissionDTO]**](ResourcePermissionDTO.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_role**
> RoleDTO get_role(role_uid)

Get a role.

Get a role for the given UID.  You need to have a permission with action `roles:read` and scope `roles:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.role_dto import RoleDTO
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
    api_instance = grafana_client.AccessControlApi(api_client)
    role_uid = 'role_uid_example' # str | 

    try:
        # Get a role.
        api_response = api_instance.get_role(role_uid)
        print("The response of AccessControlApi->get_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->get_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_uid** | **str**|  | 

### Return type

[**RoleDTO**](RoleDTO.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_role_assignments**
> RoleAssignmentsDTO get_role_assignments(role_uid)

Get role assignments.

Get role assignments for the role with the given UID.  You need to have a permission with action `teams.roles:list` and scope `teams:id:*` and `users.roles:list` and scope `users:id:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.role_assignments_dto import RoleAssignmentsDTO
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
    api_instance = grafana_client.AccessControlApi(api_client)
    role_uid = 'role_uid_example' # str | 

    try:
        # Get role assignments.
        api_response = api_instance.get_role_assignments(role_uid)
        print("The response of AccessControlApi->get_role_assignments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->get_role_assignments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_uid** | **str**|  | 

### Return type

[**RoleAssignmentsDTO**](RoleAssignmentsDTO.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_roles**
> List[RoleDTO] list_roles(delegatable=delegatable)

Get all roles.

Gets all existing roles. The response contains all global and organization local roles, for the organization which user is signed in.  You need to have a permission with action `roles:read` and scope `roles:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.role_dto import RoleDTO
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
    api_instance = grafana_client.AccessControlApi(api_client)
    delegatable = True # bool |  (optional)

    try:
        # Get all roles.
        api_response = api_instance.list_roles(delegatable=delegatable)
        print("The response of AccessControlApi->list_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->list_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **delegatable** | **bool**|  | [optional] 

### Return type

[**List[RoleDTO]**](RoleDTO.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_team_roles**
> SuccessResponseBody list_team_roles(team_id)

Get team roles.

You need to have a permission with action `teams.roles:read` and scope `teams:id:<team ID>`.

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
    api_instance = grafana_client.AccessControlApi(api_client)
    team_id = 56 # int | 

    try:
        # Get team roles.
        api_response = api_instance.list_team_roles(team_id)
        print("The response of AccessControlApi->list_team_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->list_team_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **team_id** | **int**|  | 

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
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_teams_roles**
> Dict[str, List[RoleDTO]] list_teams_roles(roles_search_query)

List roles assigned to multiple teams.

Lists the roles that have been directly assigned to the given teams.  You need to have a permission with action `teams.roles:read` and scope `teams:id:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.role_dto import RoleDTO
from grafana_client.models.roles_search_query import RolesSearchQuery
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
    api_instance = grafana_client.AccessControlApi(api_client)
    roles_search_query = grafana_client.RolesSearchQuery() # RolesSearchQuery | 

    try:
        # List roles assigned to multiple teams.
        api_response = api_instance.list_teams_roles(roles_search_query)
        print("The response of AccessControlApi->list_teams_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->list_teams_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **roles_search_query** | [**RolesSearchQuery**](RolesSearchQuery.md)|  | 

### Return type

**Dict[str, List[RoleDTO]]**

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_user_roles**
> List[RoleDTO] list_user_roles(user_id)

List roles assigned to a user.

Lists the roles that have been directly assigned to a given user. The list does not include built-in roles (Viewer, Editor, Admin or Grafana Admin), and it does not include roles that have been inherited from a team.  You need to have a permission with action `users.roles:read` and scope `users:id:<user ID>`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.role_dto import RoleDTO
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
    api_instance = grafana_client.AccessControlApi(api_client)
    user_id = 56 # int | 

    try:
        # List roles assigned to a user.
        api_response = api_instance.list_user_roles(user_id)
        print("The response of AccessControlApi->list_user_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->list_user_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **int**|  | 

### Return type

[**List[RoleDTO]**](RoleDTO.md)

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_users_roles**
> Dict[str, List[RoleDTO]] list_users_roles(roles_search_query)

List roles assigned to multiple users.

Lists the roles that have been directly assigned to the given users. The list does not include built-in roles (Viewer, Editor, Admin or Grafana Admin), and it does not include roles that have been inherited from a team.  You need to have a permission with action `users.roles:read` and scope `users:id:*`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.role_dto import RoleDTO
from grafana_client.models.roles_search_query import RolesSearchQuery
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
    api_instance = grafana_client.AccessControlApi(api_client)
    roles_search_query = grafana_client.RolesSearchQuery() # RolesSearchQuery | 

    try:
        # List roles assigned to multiple users.
        api_response = api_instance.list_users_roles(roles_search_query)
        print("The response of AccessControlApi->list_users_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->list_users_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **roles_search_query** | [**RolesSearchQuery**](RolesSearchQuery.md)|  | 

### Return type

**Dict[str, List[RoleDTO]]**

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_team_role**
> SuccessResponseBody remove_team_role(role_uid, team_id)

Remove team role.

You need to have a permission with action `teams.roles:remove` and scope `permissions:type:delegate`.

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
    api_instance = grafana_client.AccessControlApi(api_client)
    role_uid = 'role_uid_example' # str | 
    team_id = 56 # int | 

    try:
        # Remove team role.
        api_response = api_instance.remove_team_role(role_uid, team_id)
        print("The response of AccessControlApi->remove_team_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->remove_team_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_uid** | **str**|  | 
 **team_id** | **int**|  | 

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
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_user_role**
> SuccessResponseBody remove_user_role(role_uid, user_id, var_global=var_global)

Remove a user role assignment.

Revoke a role from a user. For bulk updates consider Set user role assignments.  You need to have a permission with action `users.roles:remove` and scope `permissions:type:delegate`. `permissions:type:delegate` scope ensures that users can only unassign roles which have same, or a subset of permissions which the user has. For example, if a user does not have required permissions for creating users, they won’t be able to unassign a role which will allow to do that. This is done to prevent escalation of privileges.

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
    api_instance = grafana_client.AccessControlApi(api_client)
    role_uid = 'role_uid_example' # str | 
    user_id = 56 # int | 
    var_global = True # bool | A flag indicating if the assignment is global or not. If set to false, the default org ID of the authenticated user will be used from the request to remove assignment. (optional)

    try:
        # Remove a user role assignment.
        api_response = api_instance.remove_user_role(role_uid, user_id, var_global=var_global)
        print("The response of AccessControlApi->remove_user_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->remove_user_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_uid** | **str**|  | 
 **user_id** | **int**|  | 
 **var_global** | **bool**| A flag indicating if the assignment is global or not. If set to false, the default org ID of the authenticated user will be used from the request to remove assignment. | [optional] 

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
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_resource_permissions**
> SuccessResponseBody set_resource_permissions(resource, resource_id, set_permissions_command)

Set resource permissions.

Assigns permissions for a resource by a given type (`:resource`) and `:resourceID` to one or many assignment types. Allowed resources are `datasources`, `teams`, `dashboards`, `folders`, and `serviceaccounts`. Refer to the `/access-control/{resource}/description` endpoint for allowed Permissions.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.set_permissions_command import SetPermissionsCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    resource = 'resource_example' # str | 
    resource_id = 'resource_id_example' # str | 
    set_permissions_command = grafana_client.SetPermissionsCommand() # SetPermissionsCommand | 

    try:
        # Set resource permissions.
        api_response = api_instance.set_resource_permissions(resource, resource_id, set_permissions_command)
        print("The response of AccessControlApi->set_resource_permissions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->set_resource_permissions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **resource_id** | **str**|  | 
 **set_permissions_command** | [**SetPermissionsCommand**](SetPermissionsCommand.md)|  | 

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_resource_permissions_for_built_in_role**
> SuccessResponseBody set_resource_permissions_for_built_in_role(resource, resource_id, built_in_role, set_permission_command)

Set resource permissions for a built-in role.

Assigns permissions for a resource by a given type (`:resource`) and `:resourceID` to a built-in role. Allowed resources are `datasources`, `teams`, `dashboards`, `folders`, and `serviceaccounts`. Refer to the `/access-control/{resource}/description` endpoint for allowed Permissions.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.set_permission_command import SetPermissionCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    resource = 'resource_example' # str | 
    resource_id = 'resource_id_example' # str | 
    built_in_role = 'built_in_role_example' # str | 
    set_permission_command = grafana_client.SetPermissionCommand() # SetPermissionCommand | 

    try:
        # Set resource permissions for a built-in role.
        api_response = api_instance.set_resource_permissions_for_built_in_role(resource, resource_id, built_in_role, set_permission_command)
        print("The response of AccessControlApi->set_resource_permissions_for_built_in_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->set_resource_permissions_for_built_in_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **resource_id** | **str**|  | 
 **built_in_role** | **str**|  | 
 **set_permission_command** | [**SetPermissionCommand**](SetPermissionCommand.md)|  | 

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_resource_permissions_for_team**
> SuccessResponseBody set_resource_permissions_for_team(resource, resource_id, team_id, set_permission_command)

Set resource permissions for a team.

Assigns permissions for a resource by a given type (`:resource`) and `:resourceID` to a team. Allowed resources are `datasources`, `teams`, `dashboards`, `folders`, and `serviceaccounts`. Refer to the `/access-control/{resource}/description` endpoint for allowed Permissions.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.set_permission_command import SetPermissionCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    resource = 'resource_example' # str | 
    resource_id = 'resource_id_example' # str | 
    team_id = 56 # int | 
    set_permission_command = grafana_client.SetPermissionCommand() # SetPermissionCommand | 

    try:
        # Set resource permissions for a team.
        api_response = api_instance.set_resource_permissions_for_team(resource, resource_id, team_id, set_permission_command)
        print("The response of AccessControlApi->set_resource_permissions_for_team:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->set_resource_permissions_for_team: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **resource_id** | **str**|  | 
 **team_id** | **int**|  | 
 **set_permission_command** | [**SetPermissionCommand**](SetPermissionCommand.md)|  | 

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_resource_permissions_for_user**
> SuccessResponseBody set_resource_permissions_for_user(resource, resource_id, user_id, set_permission_command)

Set resource permissions for a user.

Assigns permissions for a resource by a given type (`:resource`) and `:resourceID` to a user or a service account. Allowed resources are `datasources`, `teams`, `dashboards`, `folders`, and `serviceaccounts`. Refer to the `/access-control/{resource}/description` endpoint for allowed Permissions.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.set_permission_command import SetPermissionCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    resource = 'resource_example' # str | 
    resource_id = 'resource_id_example' # str | 
    user_id = 56 # int | 
    set_permission_command = grafana_client.SetPermissionCommand() # SetPermissionCommand | 

    try:
        # Set resource permissions for a user.
        api_response = api_instance.set_resource_permissions_for_user(resource, resource_id, user_id, set_permission_command)
        print("The response of AccessControlApi->set_resource_permissions_for_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->set_resource_permissions_for_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource** | **str**|  | 
 **resource_id** | **str**|  | 
 **user_id** | **int**|  | 
 **set_permission_command** | [**SetPermissionCommand**](SetPermissionCommand.md)|  | 

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_role_assignments**
> RoleAssignmentsDTO set_role_assignments(role_uid, set_role_assignments_command)

Set role assignments.

Set role assignments for the role with the given UID.  You need to have a permission with action `teams.roles:add` and `teams.roles:remove` and scope `permissions:type:delegate`, and `users.roles:add` and `users.roles:remove` and scope `permissions:type:delegate`.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.role_assignments_dto import RoleAssignmentsDTO
from grafana_client.models.set_role_assignments_command import SetRoleAssignmentsCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    role_uid = 'role_uid_example' # str | 
    set_role_assignments_command = grafana_client.SetRoleAssignmentsCommand() # SetRoleAssignmentsCommand | 

    try:
        # Set role assignments.
        api_response = api_instance.set_role_assignments(role_uid, set_role_assignments_command)
        print("The response of AccessControlApi->set_role_assignments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->set_role_assignments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_uid** | **str**|  | 
 **set_role_assignments_command** | [**SetRoleAssignmentsCommand**](SetRoleAssignmentsCommand.md)|  | 

### Return type

[**RoleAssignmentsDTO**](RoleAssignmentsDTO.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_team_roles**
> SuccessResponseBody set_team_roles(team_id)

Update team role.

You need to have a permission with action `teams.roles:add` and `teams.roles:remove` and scope `permissions:type:delegate` for each.

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
    api_instance = grafana_client.AccessControlApi(api_client)
    team_id = 56 # int | 

    try:
        # Update team role.
        api_response = api_instance.set_team_roles(team_id)
        print("The response of AccessControlApi->set_team_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->set_team_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **team_id** | **int**|  | 

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
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_user_roles**
> SuccessResponseBody set_user_roles(user_id, set_user_roles_command)

Set user role assignments.

Update the user’s role assignments to match the provided set of UIDs. This will remove any assigned roles that aren’t in the request and add roles that are in the set but are not already assigned to the user. If you want to add or remove a single role, consider using Add a user role assignment or Remove a user role assignment instead.  You need to have a permission with action `users.roles:add` and `users.roles:remove` and scope `permissions:type:delegate` for each. `permissions:type:delegate`  scope ensures that users can only assign or unassign roles which have same, or a subset of permissions which the user has. For example, if a user does not have required permissions for creating users, they won’t be able to assign or unassign a role which will allow to do that. This is done to prevent escalation of privileges.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.set_user_roles_command import SetUserRolesCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    user_id = 56 # int | 
    set_user_roles_command = grafana_client.SetUserRolesCommand() # SetUserRolesCommand | 

    try:
        # Set user role assignments.
        api_response = api_instance.set_user_roles(user_id, set_user_roles_command)
        print("The response of AccessControlApi->set_user_roles:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->set_user_roles: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **int**|  | 
 **set_user_roles_command** | [**SetUserRolesCommand**](SetUserRolesCommand.md)|  | 

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
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_role**
> RoleDTO update_role(role_uid, update_role_command)

Update a custom role.

You need to have a permission with action `roles:write` and scope `permissions:type:delegate`. `permissions:type:delegate` scope ensures that users can only create custom roles with the same, or a subset of permissions which the user has.

### Example

* Api Key Authentication (api_key):
* Basic Authentication (basic):

```python
import grafana_client
from grafana_client.models.role_dto import RoleDTO
from grafana_client.models.update_role_command import UpdateRoleCommand
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
    api_instance = grafana_client.AccessControlApi(api_client)
    role_uid = 'role_uid_example' # str | 
    update_role_command = grafana_client.UpdateRoleCommand() # UpdateRoleCommand | 

    try:
        # Update a custom role.
        api_response = api_instance.update_role(role_uid, update_role_command)
        print("The response of AccessControlApi->update_role:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccessControlApi->update_role: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_uid** | **str**|  | 
 **update_role_command** | [**UpdateRoleCommand**](UpdateRoleCommand.md)|  | 

### Return type

[**RoleDTO**](RoleDTO.md)

### Authorization

[api_key](../README.md#api_key), [basic](../README.md#basic)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | (empty) |  -  |
**400** | BadRequestError is returned when the request is invalid and it cannot be processed. |  -  |
**403** | ForbiddenError is returned if the user/token has insufficient permissions to access the requested resource. |  -  |
**404** | NotFoundError is returned when the requested resource was not found. |  -  |
**500** | InternalServerError is a general error indicating something went wrong internally. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

