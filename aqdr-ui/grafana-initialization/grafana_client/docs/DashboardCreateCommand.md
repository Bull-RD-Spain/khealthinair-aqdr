# DashboardCreateCommand

These are the values expected to be sent from an end user +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_version** | **str** | APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources +optional | [optional] 
**dashboard** | [**Unstructured**](Unstructured.md) |  | 
**expires** | **int** | When the snapshot should expire in seconds in seconds. Default is never to expire. | [optional] [default to 0]
**external** | **bool** | these are passed when storing an external snapshot ref Save the snapshot on an external server rather than locally. | [optional] [default to False]
**kind** | **str** | Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds +optional | [optional] 
**name** | **str** | Snapshot name | [optional] 

## Example

```python
from grafana_client.models.dashboard_create_command import DashboardCreateCommand

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardCreateCommand from a JSON string
dashboard_create_command_instance = DashboardCreateCommand.from_json(json)
# print the JSON string representation of the object
print(DashboardCreateCommand.to_json())

# convert the object into a dict
dashboard_create_command_dict = dashboard_create_command_instance.to_dict()
# create an instance of DashboardCreateCommand from a dict
dashboard_create_command_from_dict = DashboardCreateCommand.from_dict(dashboard_create_command_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


