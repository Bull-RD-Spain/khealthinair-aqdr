# AlertRuleUpgrade


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sends_to** | **List[str]** |  | [optional] 
**title** | **str** |  | [optional] 
**uid** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.alert_rule_upgrade import AlertRuleUpgrade

# TODO update the JSON string below
json = "{}"
# create an instance of AlertRuleUpgrade from a JSON string
alert_rule_upgrade_instance = AlertRuleUpgrade.from_json(json)
# print the JSON string representation of the object
print(AlertRuleUpgrade.to_json())

# convert the object into a dict
alert_rule_upgrade_dict = alert_rule_upgrade_instance.to_dict()
# create an instance of AlertRuleUpgrade from a dict
alert_rule_upgrade_from_dict = AlertRuleUpgrade.from_dict(alert_rule_upgrade_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


