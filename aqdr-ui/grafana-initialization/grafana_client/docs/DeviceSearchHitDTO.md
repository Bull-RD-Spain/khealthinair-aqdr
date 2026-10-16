# DeviceSearchHitDTO


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_ip** | **str** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**device_id** | **str** |  | [optional] 
**last_seen_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**user_agent** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.device_search_hit_dto import DeviceSearchHitDTO

# TODO update the JSON string below
json = "{}"
# create an instance of DeviceSearchHitDTO from a JSON string
device_search_hit_dto_instance = DeviceSearchHitDTO.from_json(json)
# print the JSON string representation of the object
print(DeviceSearchHitDTO.to_json())

# convert the object into a dict
device_search_hit_dto_dict = device_search_hit_dto_instance.to_dict()
# create an instance of DeviceSearchHitDTO from a dict
device_search_hit_dto_from_dict = DeviceSearchHitDTO.from_dict(device_search_hit_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


