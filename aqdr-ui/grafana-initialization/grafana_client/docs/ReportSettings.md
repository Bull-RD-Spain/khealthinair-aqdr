# ReportSettings


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**branding** | [**ReportBrandingOptions**](ReportBrandingOptions.md) |  | [optional] 
**id** | **int** |  | [optional] 
**org_id** | **int** |  | [optional] 
**user_id** | **int** |  | [optional] 

## Example

```python
from grafana_client.models.report_settings import ReportSettings

# TODO update the JSON string below
json = "{}"
# create an instance of ReportSettings from a JSON string
report_settings_instance = ReportSettings.from_json(json)
# print the JSON string representation of the object
print(ReportSettings.to_json())

# convert the object into a dict
report_settings_dict = report_settings_instance.to_dict()
# create an instance of ReportSettings from a dict
report_settings_from_dict = ReportSettings.from_dict(report_settings_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


