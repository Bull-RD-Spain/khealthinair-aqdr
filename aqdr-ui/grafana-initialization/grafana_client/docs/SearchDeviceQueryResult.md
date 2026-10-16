# SearchDeviceQueryResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**devices** | [**List[DeviceSearchHitDTO]**](DeviceSearchHitDTO.md) |  | [optional] 
**page** | **int** |  | [optional] 
**per_page** | **int** |  | [optional] 
**total_count** | **int** |  | [optional] 

## Example

```python
from grafana_client.models.search_device_query_result import SearchDeviceQueryResult

# TODO update the JSON string below
json = "{}"
# create an instance of SearchDeviceQueryResult from a JSON string
search_device_query_result_instance = SearchDeviceQueryResult.from_json(json)
# print the JSON string representation of the object
print(SearchDeviceQueryResult.to_json())

# convert the object into a dict
search_device_query_result_dict = search_device_query_result_instance.to_dict()
# create an instance of SearchDeviceQueryResult from a dict
search_device_query_result_from_dict = SearchDeviceQueryResult.from_dict(search_device_query_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


