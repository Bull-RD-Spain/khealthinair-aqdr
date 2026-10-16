# PostableTimeIntervals


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**time_intervals** | [**List[TimeIntervalItem]**](TimeIntervalItem.md) |  | [optional] 

## Example

```python
from grafana_client.models.postable_time_intervals import PostableTimeIntervals

# TODO update the JSON string below
json = "{}"
# create an instance of PostableTimeIntervals from a JSON string
postable_time_intervals_instance = PostableTimeIntervals.from_json(json)
# print the JSON string representation of the object
print(PostableTimeIntervals.to_json())

# convert the object into a dict
postable_time_intervals_dict = postable_time_intervals_instance.to_dict()
# create an instance of PostableTimeIntervals from a dict
postable_time_intervals_from_dict = PostableTimeIntervals.from_dict(postable_time_intervals_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


