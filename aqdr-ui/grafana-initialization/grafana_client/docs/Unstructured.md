# Unstructured

Unstructured allows objects that do not have Golang structs registered to be manipulated generically.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**object** | **object** | Object is a JSON compatible map with string, float, int, bool, []interface{}, or map[string]interface{} children. | [optional] 

## Example

```python
from grafana_client.models.unstructured import Unstructured

# TODO update the JSON string below
json = "{}"
# create an instance of Unstructured from a JSON string
unstructured_instance = Unstructured.from_json(json)
# print the JSON string representation of the object
print(Unstructured.to_json())

# convert the object into a dict
unstructured_dict = unstructured_instance.to_dict()
# create an instance of Unstructured from a dict
unstructured_from_dict = Unstructured.from_dict(unstructured_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


