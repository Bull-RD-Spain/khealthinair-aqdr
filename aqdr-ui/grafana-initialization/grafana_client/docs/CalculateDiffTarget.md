# CalculateDiffTarget


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboard_id** | **int** |  | [optional] 
**unsaved_dashboard** | **object** |  | [optional] 
**version** | **int** |  | [optional] 

## Example

```python
from grafana_client.models.calculate_diff_target import CalculateDiffTarget

# TODO update the JSON string below
json = "{}"
# create an instance of CalculateDiffTarget from a JSON string
calculate_diff_target_instance = CalculateDiffTarget.from_json(json)
# print the JSON string representation of the object
print(CalculateDiffTarget.to_json())

# convert the object into a dict
calculate_diff_target_dict = calculate_diff_target_instance.to_dict()
# create an instance of CalculateDiffTarget from a dict
calculate_diff_target_from_dict = CalculateDiffTarget.from_dict(calculate_diff_target_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


