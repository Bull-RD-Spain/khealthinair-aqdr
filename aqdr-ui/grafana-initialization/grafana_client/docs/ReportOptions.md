# ReportOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**layout** | **str** |  | [optional] 
**orientation** | **str** |  | [optional] 
**time_range** | [**ReportTimeRange**](ReportTimeRange.md) |  | [optional] 

## Example

```python
from grafana_client.models.report_options import ReportOptions

# TODO update the JSON string below
json = "{}"
# create an instance of ReportOptions from a JSON string
report_options_instance = ReportOptions.from_json(json)
# print the JSON string representation of the object
print(ReportOptions.to_json())

# convert the object into a dict
report_options_dict = report_options_instance.to_dict()
# create an instance of ReportOptions from a dict
report_options_from_dict = ReportOptions.from_dict(report_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


