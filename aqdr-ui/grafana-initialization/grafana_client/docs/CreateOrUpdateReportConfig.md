# CreateOrUpdateReportConfig


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboard_id** | **int** |  | [optional] 
**dashboard_uid** | **str** |  | [optional] 
**dashboards** | [**List[ReportDashboard]**](ReportDashboard.md) |  | [optional] 
**enable_csv** | **bool** |  | [optional] 
**enable_dashboard_url** | **bool** |  | [optional] 
**formats** | **List[str]** |  | [optional] 
**message** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**options** | [**ReportOptions**](ReportOptions.md) |  | [optional] 
**recipients** | **str** |  | [optional] 
**reply_to** | **str** |  | [optional] 
**scale_factor** | **int** |  | [optional] 
**schedule** | [**ReportSchedule**](ReportSchedule.md) |  | [optional] 
**state** | **str** |  | [optional] 
**template_vars** | **object** |  | [optional] 

## Example

```python
from grafana_client.models.create_or_update_report_config import CreateOrUpdateReportConfig

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrUpdateReportConfig from a JSON string
create_or_update_report_config_instance = CreateOrUpdateReportConfig.from_json(json)
# print the JSON string representation of the object
print(CreateOrUpdateReportConfig.to_json())

# convert the object into a dict
create_or_update_report_config_dict = create_or_update_report_config_instance.to_dict()
# create an instance of CreateOrUpdateReportConfig from a dict
create_or_update_report_config_from_dict = CreateOrUpdateReportConfig.from_dict(create_or_update_report_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


