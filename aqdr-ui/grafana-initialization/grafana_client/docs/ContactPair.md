# ContactPair


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**contact_point** | [**ContactPointUpgrade**](ContactPointUpgrade.md) |  | [optional] 
**error** | **str** |  | [optional] 
**legacy_channel** | [**LegacyChannel**](LegacyChannel.md) |  | [optional] 

## Example

```python
from grafana_client.models.contact_pair import ContactPair

# TODO update the JSON string below
json = "{}"
# create an instance of ContactPair from a JSON string
contact_pair_instance = ContactPair.from_json(json)
# print the JSON string representation of the object
print(ContactPair.to_json())

# convert the object into a dict
contact_pair_dict = contact_pair_instance.to_dict()
# create an instance of ContactPair from a dict
contact_pair_from_dict = ContactPair.from_dict(contact_pair_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


