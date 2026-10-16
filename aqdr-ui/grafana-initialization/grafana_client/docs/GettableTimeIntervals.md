# GettableTimeIntervals


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**provenance** | **str** |  | [optional] 
**time_intervals** | [**List[TimeIntervalItem]**](TimeIntervalItem.md) |  | [optional] 

## Example

```python
from grafana_client.models.gettable_time_intervals import GettableTimeIntervals

# TODO update the JSON string below
json = "{}"
# create an instance of GettableTimeIntervals from a JSON string
gettable_time_intervals_instance = GettableTimeIntervals.from_json(json)
# print the JSON string representation of the object
print(GettableTimeIntervals.to_json())

# convert the object into a dict
gettable_time_intervals_dict = gettable_time_intervals_instance.to_dict()
# create an instance of GettableTimeIntervals from a dict
gettable_time_intervals_from_dict = GettableTimeIntervals.from_dict(gettable_time_intervals_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


