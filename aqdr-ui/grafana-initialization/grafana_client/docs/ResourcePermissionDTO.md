# ResourcePermissionDTO


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actions** | **List[str]** |  | [optional] 
**built_in_role** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**is_inherited** | **bool** |  | [optional] 
**is_managed** | **bool** |  | [optional] 
**is_service_account** | **bool** |  | [optional] 
**permission** | **str** |  | [optional] 
**role_name** | **str** |  | [optional] 
**team** | **str** |  | [optional] 
**team_avatar_url** | **str** |  | [optional] 
**team_id** | **int** |  | [optional] 
**user_avatar_url** | **str** |  | [optional] 
**user_id** | **int** |  | [optional] 
**user_login** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.resource_permission_dto import ResourcePermissionDTO

# TODO update the JSON string below
json = "{}"
# create an instance of ResourcePermissionDTO from a JSON string
resource_permission_dto_instance = ResourcePermissionDTO.from_json(json)
# print the JSON string representation of the object
print(ResourcePermissionDTO.to_json())

# convert the object into a dict
resource_permission_dto_dict = resource_permission_dto_instance.to_dict()
# create an instance of ResourcePermissionDTO from a dict
resource_permission_dto_from_dict = ResourcePermissionDTO.from_dict(resource_permission_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


