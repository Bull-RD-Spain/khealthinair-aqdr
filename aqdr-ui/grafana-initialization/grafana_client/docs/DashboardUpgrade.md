# DashboardUpgrade


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboard_id** | **int** |  | [optional] 
**dashboard_name** | **str** |  | [optional] 
**dashboard_uid** | **str** |  | [optional] 
**error** | **str** |  | [optional] 
**folder_name** | **str** |  | [optional] 
**folder_uid** | **str** |  | [optional] 
**migrated_alerts** | [**List[AlertPair]**](AlertPair.md) |  | [optional] 
**new_folder_name** | **str** |  | [optional] 
**new_folder_uid** | **str** |  | [optional] 
**provisioned** | **bool** |  | [optional] 
**warning** | **str** |  | [optional] 

## Example

```python
from grafana_client.models.dashboard_upgrade import DashboardUpgrade

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardUpgrade from a JSON string
dashboard_upgrade_instance = DashboardUpgrade.from_json(json)
# print the JSON string representation of the object
print(DashboardUpgrade.to_json())

# convert the object into a dict
dashboard_upgrade_dict = dashboard_upgrade_instance.to_dict()
# create an instance of DashboardUpgrade from a dict
dashboard_upgrade_from_dict = DashboardUpgrade.from_dict(dashboard_upgrade_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


