# OrgMigrationSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_errors** | **bool** |  | [optional] 
**new_alerts** | **int** |  | [optional] 
**new_channels** | **int** |  | [optional] 
**new_dashboards** | **int** |  | [optional] 
**removed** | **bool** |  | [optional] 

## Example

```python
from grafana_client.models.org_migration_summary import OrgMigrationSummary

# TODO update the JSON string below
json = "{}"
# create an instance of OrgMigrationSummary from a JSON string
org_migration_summary_instance = OrgMigrationSummary.from_json(json)
# print the JSON string representation of the object
print(OrgMigrationSummary.to_json())

# convert the object into a dict
org_migration_summary_dict = org_migration_summary_instance.to_dict()
# create an instance of OrgMigrationSummary from a dict
org_migration_summary_from_dict = OrgMigrationSummary.from_dict(org_migration_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


