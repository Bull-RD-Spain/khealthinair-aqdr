# ServiceAccountProfileDTO


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_control** | **Dict[str, bool]** |  | [optional] 
**avatar_url** | **str** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**id** | **int** |  | [optional] 
**is_disabled** | **bool** |  | [optional] 
**is_external** | **bool** |  | [optional] 
**login** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**org_id** | **int** |  | [optional] 
**required_by** | **str** |  | [optional] 
**role** | **str** |  | [optional] 
**teams** | **List[str]** |  | [optional] 
**tokens** | **int** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from grafana_client.models.service_account_profile_dto import ServiceAccountProfileDTO

# TODO update the JSON string below
json = "{}"
# create an instance of ServiceAccountProfileDTO from a JSON string
service_account_profile_dto_instance = ServiceAccountProfileDTO.from_json(json)
# print the JSON string representation of the object
print(ServiceAccountProfileDTO.to_json())

# convert the object into a dict
service_account_profile_dto_dict = service_account_profile_dto_instance.to_dict()
# create an instance of ServiceAccountProfileDTO from a dict
service_account_profile_dto_from_dict = ServiceAccountProfileDTO.from_dict(service_account_profile_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


