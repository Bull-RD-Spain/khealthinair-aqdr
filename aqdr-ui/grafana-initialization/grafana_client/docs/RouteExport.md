# RouteExport

RouteExport is the provisioned file export of definitions.Route. This is needed to hide fields that aren't useable in provisioning file format. An alternative would be to define a custom MarshalJSON and MarshalYAML that excludes them.

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
**receiver** | **str** |  | [optional] 
**repeat_interval** | **str** |  | [optional] 
**routes** | [**List[RouteExport]**](RouteExport.md) |  | [optional] 

## Example

```python
from grafana_client.models.route_export import RouteExport

# TODO update the JSON string below
json = "{}"
# create an instance of RouteExport from a JSON string
route_export_instance = RouteExport.from_json(json)
# print the JSON string representation of the object
print(RouteExport.to_json())

# convert the object into a dict
route_export_dict = route_export_instance.to_dict()
# create an instance of RouteExport from a dict
route_export_from_dict = RouteExport.from_dict(route_export_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


