# NotificationPolicyExport


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_continue** | **bool** |  | [optional] 
**group_by** | **List[str]** |  | [optional] 
**group_interval** | **str** |  | [optional] 
**group_wait** | **str** |  | [optional] 
**match** | **Dict[str, str]** | Deprecated. Remove before v1.0 release. | [optional] 
**match_re** | **Dict[str, str]** |  | [optional] 
**matchers** | [**List[Matcher]**](Matcher.md) | Matchers is a slice of Matchers that is sortable, implements Stringer, and provides a Matches method to match a LabelSet against all Matchers in the slice. Note that some users of Matchers might require it to be sorted. | [optional] 
**mute_time_intervals** | **List[str]** |  | [optional] 
**object_matchers** | **List[List[str]]** |  | [optional] 
**org_id** | **int** |  | [optional] 
**receiver** | **str** |  | [optional] 
**repeat_interval** | **str** |  | [optional] 
**routes** | [**List[RouteExport]**](RouteExport.md) |  | [optional] 

## Example

```python
from grafana_client.models.notification_policy_export import NotificationPolicyExport

# TODO update the JSON string below
json = "{}"
# create an instance of NotificationPolicyExport from a JSON string
notification_policy_export_instance = NotificationPolicyExport.from_json(json)
# print the JSON string representation of the object
print(NotificationPolicyExport.to_json())

# convert the object into a dict
notification_policy_export_dict = notification_policy_export_instance.to_dict()
# create an instance of NotificationPolicyExport from a dict
notification_policy_export_from_dict = NotificationPolicyExport.from_dict(notification_policy_export_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


