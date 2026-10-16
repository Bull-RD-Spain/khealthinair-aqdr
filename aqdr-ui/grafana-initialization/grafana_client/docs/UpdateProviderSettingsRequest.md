# UpdateProviderSettingsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**provider** | **str** |  | [optional] 
**settings** | **object** |  | [optional] 

## Example

```python
from grafana_client.models.update_provider_settings_request import UpdateProviderSettingsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateProviderSettingsRequest from a JSON string
update_provider_settings_request_instance = UpdateProviderSettingsRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateProviderSettingsRequest.to_json())

# convert the object into a dict
update_provider_settings_request_dict = update_provider_settings_request_instance.to_dict()
# create an instance of UpdateProviderSettingsRequest from a dict
update_provider_settings_request_from_dict = UpdateProviderSettingsRequest.from_dict(update_provider_settings_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


