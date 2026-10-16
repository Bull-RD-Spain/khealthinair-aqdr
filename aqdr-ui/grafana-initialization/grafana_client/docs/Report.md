# Report

ConfigDTO is model representation in transfer

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created** | **datetime** |  | [optional] 
**dashboard_id** | **int** |  | [optional] 
**dashboard_name** | **str** |  | [optional] 
**dashboard_uid** | **str** |  | [optional] 
**dashboards** | [**List[ReportDashboard]**](ReportDashboard.md) |  | [optional] 
**enable_csv** | **bool** |  | [optional] 
**enable_dashboard_url** | **bool** |  | [optional] 
**formats** | **List[str]** |  | [optional] 
**id** | **int** |  | [optional] 
**message** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**options** | [**ReportOptions**](ReportOptions.md) |  | [optional] 
**org_id** | **int** |  | [optional] 
**recipients** | **str** |  | [optional] 
**reply_to** | **str** |  | [optional] 
**scale_factor** | **int** |  | [optional] 
**schedule** | [**ReportSchedule**](ReportSchedule.md) |  | [optional] 
**state** | **str** |  | [optional] 
**template_vars** | **object** |  | [optional] 
**updated** | **datetime** |  | [optional] 
**user_id** | **int** |  | [optional] 

## Example

```python
from grafana_client.models.report import Report

# TODO update the JSON string below
json = "{}"
# create an instance of Report from a JSON string
report_instance = Report.from_json(json)
# print the JSON string representation of the object
print(Report.to_json())

# convert the object into a dict
report_dict = report_instance.to_dict()
# create an instance of Report from a dict
report_from_dict = Report.from_dict(report_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


