# PostableGrafanaReceivers


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grafana_managed_receiver_configs** | [**List[PostableGrafanaReceiver]**](PostableGrafanaReceiver.md) |  | [optional] 

## Example

```python
from grafana_client.models.postable_grafana_receivers import PostableGrafanaReceivers

# TODO update the JSON string below
json = "{}"
# create an instance of PostableGrafanaReceivers from a JSON string
postable_grafana_receivers_instance = PostableGrafanaReceivers.from_json(json)
# print the JSON string representation of the object
print(PostableGrafanaReceivers.to_json())

# convert the object into a dict
postable_grafana_receivers_dict = postable_grafana_receivers_instance.to_dict()
# create an instance of PostableGrafanaReceivers from a dict
postable_grafana_receivers_from_dict = PostableGrafanaReceivers.from_dict(postable_grafana_receivers_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


