# AlertPair


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alert_rule** | [**AlertRuleUpgrade**](AlertRuleUpgrade.md) |  | [optional] 
**error** | **str** |  | [optional] 
**legacy_alert** | [**LegacyAlert**](LegacyAlert.md) |  | [optional] 

## Example

```python
from grafana_client.models.alert_pair import AlertPair

# TODO update the JSON string below
json = "{}"
# create an instance of AlertPair from a JSON string
alert_pair_instance = AlertPair.from_json(json)
# print the JSON string representation of the object
print(AlertPair.to_json())

# convert the object into a dict
alert_pair_dict = alert_pair_instance.to_dict()
# create an instance of AlertPair from a dict
alert_pair_from_dict = AlertPair.from_dict(alert_pair_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


