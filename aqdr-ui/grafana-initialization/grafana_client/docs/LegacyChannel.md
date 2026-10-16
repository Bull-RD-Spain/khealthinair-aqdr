# LegacyChannel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**type** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.legacy_channel import LegacyChannel

# TODO update the JSON string below
json = "{}"
# create an instance of LegacyChannel from a JSON string
legacy_channel_instance = LegacyChannel.from_json(json)
# print the JSON string representation of the object
print(LegacyChannel.to_json())

# convert the object into a dict
legacy_channel_dict = legacy_channel_instance.to_dict()
# create an instance of LegacyChannel from a dict
legacy_channel_from_dict = LegacyChannel.from_dict(legacy_channel_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


