# ReportTimeRange


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_from** | **str** |  | [optional] 
**to** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.report_time_range import ReportTimeRange

# TODO update the JSON string below
json = "{}"
# create an instance of ReportTimeRange from a JSON string
report_time_range_instance = ReportTimeRange.from_json(json)
# print the JSON string representation of the object
print(ReportTimeRange.to_json())

# convert the object into a dict
report_time_range_dict = report_time_range_instance.to_dict()
# create an instance of ReportTimeRange from a dict
report_time_range_from_dict = ReportTimeRange.from_dict(report_time_range_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


