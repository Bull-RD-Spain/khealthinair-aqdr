# ContactPointUpgrade


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**route_matchers** | **List[List[str]]** |  | [optional] 
**type** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.contact_point_upgrade import ContactPointUpgrade

# TODO update the JSON string below
json = "{}"
# create an instance of ContactPointUpgrade from a JSON string
contact_point_upgrade_instance = ContactPointUpgrade.from_json(json)
# print the JSON string representation of the object
print(ContactPointUpgrade.to_json())

# convert the object into a dict
contact_point_upgrade_dict = contact_point_upgrade_instance.to_dict()
# create an instance of ContactPointUpgrade from a dict
contact_point_upgrade_from_dict = ContactPointUpgrade.from_dict(contact_point_upgrade_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


