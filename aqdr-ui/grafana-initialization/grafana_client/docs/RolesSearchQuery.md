# RolesSearchQuery


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**include_hidden** | **bool** |  | [optional] 
**org_id** | **int** |  | [optional] 
**team_ids** | **List[int]** |  | [optional] 
**user_ids** | **List[int]** |  | [optional] 

## Example

```python
from grafana_client.models.roles_search_query import RolesSearchQuery

# TODO update the JSON string below
json = "{}"
# create an instance of RolesSearchQuery from a JSON string
roles_search_query_instance = RolesSearchQuery.from_json(json)
# print the JSON string representation of the object
print(RolesSearchQuery.to_json())

# convert the object into a dict
roles_search_query_dict = roles_search_query_instance.to_dict()
# create an instance of RolesSearchQuery from a dict
roles_search_query_from_dict = RolesSearchQuery.from_dict(roles_search_query_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


