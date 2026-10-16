# Preferences

Spec defines user, team or org Grafana preferences

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cookie_preferences** | [**CookiePreferences**](CookiePreferences.md) |  | [optional] 
**home_dashboard_uid** | **str** | UID for the home dashboard | [optional] 
**language** | **str** | Selected language (beta) | [optional] 
**query_history** | [**QueryHistoryPreference**](QueryHistoryPreference.md) |  | [optional] 
**theme** | **str** | Theme light, dark, empty is default | [optional] 
**timezone** | **str** | The timezone selection TODO: this should use the timezone defined in common | [optional] 
**week_start** | **str** | WeekStart day of the week (sunday, monday, etc) | [optional] 

## Example

```python
from grafana_client.models.preferences import Preferences

# TODO update the JSON string below
json = "{}"
# create an instance of Preferences from a JSON string
preferences_instance = Preferences.from_json(json)
# print the JSON string representation of the object
print(Preferences.to_json())

# convert the object into a dict
preferences_dict = preferences_instance.to_dict()
# create an instance of Preferences from a dict
preferences_from_dict = Preferences.from_dict(preferences_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


