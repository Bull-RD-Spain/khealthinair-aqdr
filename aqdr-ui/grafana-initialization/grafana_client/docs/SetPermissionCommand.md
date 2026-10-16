# SetPermissionCommand


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**permission** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.set_permission_command import SetPermissionCommand

# TODO update the JSON string below
json = "{}"
# create an instance of SetPermissionCommand from a JSON string
set_permission_command_instance = SetPermissionCommand.from_json(json)
# print the JSON string representation of the object
print(SetPermissionCommand.to_json())

# convert the object into a dict
set_permission_command_dict = set_permission_command_instance.to_dict()
# create an instance of SetPermissionCommand from a dict
set_permission_command_from_dict = SetPermissionCommand.from_dict(set_permission_command_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


