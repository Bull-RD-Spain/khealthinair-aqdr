# ReportBrandingOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email_footer_link** | **str** |  | [optional] 
**email_footer_mode** | **str** |  | [optional] 
**email_footer_text** | **str** |  | [optional] 
**email_logo_url** | **str** |  | [optional] 
**report_logo_url** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.report_branding_options import ReportBrandingOptions

# TODO update the JSON string below
json = "{}"
# create an instance of ReportBrandingOptions from a JSON string
report_branding_options_instance = ReportBrandingOptions.from_json(json)
# print the JSON string representation of the object
print(ReportBrandingOptions.to_json())

# convert the object into a dict
report_branding_options_dict = report_branding_options_instance.to_dict()
# create an instance of ReportBrandingOptions from a dict
report_branding_options_from_dict = ReportBrandingOptions.from_dict(report_branding_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


