# TimeIntervalItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**days_of_month** | **List[str]** |  | [optional] 
**location** | **str** |  | [optional] 
**months** | **List[str]** |  | [optional] 
**times** | [**List[TimeIntervalTimeRange]**](TimeIntervalTimeRange.md) |  | [optional] 
**weekdays** | **List[str]** |  | [optional] 
**years** | **List[str]** |  | [optional] 

## Example

```python
from grafana_client.models.time_interval_item import TimeIntervalItem

# TODO update the JSON string below
json = "{}"
# create an instance of TimeIntervalItem from a JSON string
time_interval_item_instance = TimeIntervalItem.from_json(json)
# print the JSON string representation of the object
print(TimeIntervalItem.to_json())

# convert the object into a dict
time_interval_item_dict = time_interval_item_instance.to_dict()
# create an instance of TimeIntervalItem from a dict
time_interval_item_from_dict = TimeIntervalItem.from_dict(time_interval_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


