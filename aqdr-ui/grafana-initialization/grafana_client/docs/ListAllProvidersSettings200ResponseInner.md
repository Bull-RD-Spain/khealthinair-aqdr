# ListAllProvidersSettings200ResponseInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**provider** | **str** |  | [optional] 
**settings** | **object** |  | [optional] 
**source** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.list_all_providers_settings200_response_inner import ListAllProvidersSettings200ResponseInner

# TODO update the JSON string below
json = "{}"
# create an instance of ListAllProvidersSettings200ResponseInner from a JSON string
list_all_providers_settings200_response_inner_instance = ListAllProvidersSettings200ResponseInner.from_json(json)
# print the JSON string representation of the object
print(ListAllProvidersSettings200ResponseInner.to_json())

# convert the object into a dict
list_all_providers_settings200_response_inner_dict = list_all_providers_settings200_response_inner_instance.to_dict()
# create an instance of ListAllProvidersSettings200ResponseInner from a dict
list_all_providers_settings200_response_inner_from_dict = ListAllProvidersSettings200ResponseInner.from_dict(list_all_providers_settings200_response_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


