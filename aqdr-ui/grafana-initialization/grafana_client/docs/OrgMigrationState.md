# OrgMigrationState


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**migrated_channels** | [**List[ContactPair]**](ContactPair.md) |  | [optional] 
**migrated_dashboards** | [**List[DashboardUpgrade]**](DashboardUpgrade.md) |  | [optional] 
**org_id** | **int** |  | [optional] 

## Example

```python
from grafana_client.models.org_migration_state import OrgMigrationState

# TODO update the JSON string below
json = "{}"
# create an instance of OrgMigrationState from a JSON string
org_migration_state_instance = OrgMigrationState.from_json(json)
# print the JSON string representation of the object
print(OrgMigrationState.to_json())

# convert the object into a dict
org_migration_state_dict = org_migration_state_instance.to_dict()
# create an instance of OrgMigrationState from a dict
org_migration_state_from_dict = OrgMigrationState.from_dict(org_migration_state_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


