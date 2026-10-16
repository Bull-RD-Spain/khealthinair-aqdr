# CreateDashboardSnapshotCommand


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_version** | **str** | APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources +optional | [optional] 
**dashboard** | [**Unstructured**](Unstructured.md) |  | 
**delete_key** | **str** | Unique key used to delete the snapshot. It is different from the &#x60;key&#x60; so that only the creator can delete the snapshot. Required if &#x60;external&#x60; is &#x60;true&#x60;. | [optional] 
**expires** | **int** | When the snapshot should expire in seconds in seconds. Default is never to expire. | [optional] [default to 0]
**external** | **bool** | these are passed when storing an external snapshot ref Save the snapshot on an external server rather than locally. | [optional] [default to False]
**key** | **str** | Define the unique key. Required if &#x60;external&#x60; is &#x60;true&#x60;. | [optional] 
**kind** | **str** | Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds +optional | [optional] 
**name** | **str** | Snapshot name | [optional] 

## Example

```python
from grafana_client.models.create_dashboard_snapshot_command import CreateDashboardSnapshotCommand

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDashboardSnapshotCommand from a JSON string
create_dashboard_snapshot_command_instance = CreateDashboardSnapshotCommand.from_json(json)
# print the JSON string representation of the object
print(CreateDashboardSnapshotCommand.to_json())

# convert the object into a dict
create_dashboard_snapshot_command_dict = create_dashboard_snapshot_command_instance.to_dict()
# create an instance of CreateDashboardSnapshotCommand from a dict
create_dashboard_snapshot_command_from_dict = CreateDashboardSnapshotCommand.from_dict(create_dashboard_snapshot_command_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


