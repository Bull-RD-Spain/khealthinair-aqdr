# SetPermissionsCommand


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**permissions** | [**List[SetResourcePermissionCommand]**](SetResourcePermissionCommand.md) |  | [optional] 

## Example

```python
from grafana_client.models.set_permissions_command import SetPermissionsCommand

# TODO update the JSON string below
json = "{}"
# create an instance of SetPermissionsCommand from a JSON string
set_permissions_command_instance = SetPermissionsCommand.from_json(json)
# print the JSON string representation of the object
print(SetPermissionsCommand.to_json())

# convert the object into a dict
set_permissions_command_dict = set_permissions_command_instance.to_dict()
# create an instance of SetPermissionsCommand from a dict
set_permissions_command_from_dict = SetPermissionsCommand.from_dict(set_permissions_command_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


