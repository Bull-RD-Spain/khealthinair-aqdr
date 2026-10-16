# MuteTimeIntervalExport


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**org_id** | **int** |  | [optional] 
**time_intervals** | [**List[TimeInterval]**](TimeInterval.md) |  | [optional] 

## Example

```python
from grafana_client.models.mute_time_interval_export import MuteTimeIntervalExport

# TODO update the JSON string below
json = "{}"
# create an instance of MuteTimeIntervalExport from a JSON string
mute_time_interval_export_instance = MuteTimeIntervalExport.from_json(json)
# print the JSON string representation of the object
print(MuteTimeIntervalExport.to_json())

# convert the object into a dict
mute_time_interval_export_dict = mute_time_interval_export_instance.to_dict()
# create an instance of MuteTimeIntervalExport from a dict
mute_time_interval_export_from_dict = MuteTimeIntervalExport.from_dict(mute_time_interval_export_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


