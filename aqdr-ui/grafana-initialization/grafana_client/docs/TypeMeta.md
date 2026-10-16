# TypeMeta

+k8s:deepcopy-gen=false

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_version** | **str** | APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources +optional | [optional] 
**kind** | **str** | Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds +optional | [optional] 

## Example

```python
from grafana_client.models.type_meta import TypeMeta

# TODO update the JSON string below
json = "{}"
# create an instance of TypeMeta from a JSON string
type_meta_instance = TypeMeta.from_json(json)
# print the JSON string representation of the object
print(TypeMeta.to_json())

# convert the object into a dict
type_meta_dict = type_meta_instance.to_dict()
# create an instance of TypeMeta from a dict
type_meta_from_dict = TypeMeta.from_dict(type_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


