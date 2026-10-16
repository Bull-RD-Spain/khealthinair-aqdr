# ReportDashboardID


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**uid** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.report_dashboard_id import ReportDashboardID

# TODO update the JSON string below
json = "{}"
# create an instance of ReportDashboardID from a JSON string
report_dashboard_id_instance = ReportDashboardID.from_json(json)
# print the JSON string representation of the object
print(ReportDashboardID.to_json())

# convert the object into a dict
report_dashboard_id_dict = report_dashboard_id_instance.to_dict()
# create an instance of ReportDashboardID from a dict
report_dashboard_id_from_dict = ReportDashboardID.from_dict(report_dashboard_id_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


