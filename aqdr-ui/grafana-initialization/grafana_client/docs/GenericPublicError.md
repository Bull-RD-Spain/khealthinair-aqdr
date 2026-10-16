# GenericPublicError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | [**PublicError**](PublicError.md) |  | [optional] 

## Example

```python
from grafana_client.models.generic_public_error import GenericPublicError

# TODO update the JSON string below
json = "{}"
# create an instance of GenericPublicError from a JSON string
generic_public_error_instance = GenericPublicError.from_json(json)
# print the JSON string representation of the object
print(GenericPublicError.to_json())

# convert the object into a dict
generic_public_error_dict = generic_public_error_instance.to_dict()
# create an instance of GenericPublicError from a dict
generic_public_error_from_dict = GenericPublicError.from_dict(generic_public_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


