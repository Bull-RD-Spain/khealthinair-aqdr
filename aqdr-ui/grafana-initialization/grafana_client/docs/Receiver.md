# Receiver


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | active | 
**integrations** | [**List[Integration]**](Integration.md) | integrations | 
**name** | **str** | name | 

## Example

```python
from grafana_client.models.receiver import Receiver

# TODO update the JSON string below
json = "{}"
# create an instance of Receiver from a JSON string
receiver_instance = Receiver.from_json(json)
# print the JSON string representation of the object
print(Receiver.to_json())

# convert the object into a dict
receiver_dict = receiver_instance.to_dict()
# create an instance of Receiver from a dict
receiver_from_dict = Receiver.from_dict(receiver_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


