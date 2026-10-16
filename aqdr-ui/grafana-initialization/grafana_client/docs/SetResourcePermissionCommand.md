# SetResourcePermissionCommand


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**built_in_role** | **str** |  | [optional] 
**permission** | **str** |  | [optional] 
**team_id** | **int** |  | [optional] 
**user_id** | **int** |  | [optional] 

## Example

```python
from grafana_client.models.set_resource_permission_command import SetResourcePermissionCommand

# TODO update the JSON string below
json = "{}"
# create an instance of SetResourcePermissionCommand from a JSON string
set_resource_permission_command_instance = SetResourcePermissionCommand.from_json(json)
# print the JSON string representation of the object
print(SetResourcePermissionCommand.to_json())

# convert the object into a dict
set_resource_permission_command_dict = set_resource_permission_command_instance.to_dict()
# create an instance of SetResourcePermissionCommand from a dict
set_resource_permission_command_from_dict = SetResourcePermissionCommand.from_dict(set_resource_permission_command_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


