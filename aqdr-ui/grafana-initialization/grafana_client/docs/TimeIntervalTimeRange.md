# TimeIntervalTimeRange


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**end_time** | **str** |  | [optional] 
**start_time** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.time_interval_time_range import TimeIntervalTimeRange

# TODO update the JSON string below
json = "{}"
# create an instance of TimeIntervalTimeRange from a JSON string
time_interval_time_range_instance = TimeIntervalTimeRange.from_json(json)
# print the JSON string representation of the object
print(TimeIntervalTimeRange.to_json())

# convert the object into a dict
time_interval_time_range_dict = time_interval_time_range_instance.to_dict()
# create an instance of TimeIntervalTimeRange from a dict
time_interval_time_range_from_dict = TimeIntervalTimeRange.from_dict(time_interval_time_range_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


