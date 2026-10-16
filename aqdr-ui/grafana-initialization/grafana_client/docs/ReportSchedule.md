# ReportSchedule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**day** | **str** |  | [optional] 
**day_of_month** | **str** |  | [optional] 
**end_date** | **datetime** |  | [optional] 
**frequency** | **str** |  | [optional] 
**hour** | **int** |  | [optional] 
**interval_amount** | **int** |  | [optional] 
**interval_frequency** | **str** |  | [optional] 
**minute** | **int** |  | [optional] 
**start_date** | **datetime** |  | [optional] 
**time_zone** | **str** |  | [optional] 
**workdays_only** | **bool** |  | [optional] 

## Example

```python
from grafana_client.models.report_schedule import ReportSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of ReportSchedule from a JSON string
report_schedule_instance = ReportSchedule.from_json(json)
# print the JSON string representation of the object
print(ReportSchedule.to_json())

# convert the object into a dict
report_schedule_dict = report_schedule_instance.to_dict()
# create an instance of ReportSchedule from a dict
report_schedule_from_dict = ReportSchedule.from_dict(report_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


