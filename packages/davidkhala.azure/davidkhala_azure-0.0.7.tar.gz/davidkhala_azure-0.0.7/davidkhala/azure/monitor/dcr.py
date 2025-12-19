from dataclasses import dataclass
from typing import Dict, List, Iterable

from azure.mgmt.monitor.models import (
    StreamDeclaration,
    DataCollectionRuleResource, DataCollectionRuleDestinations, DataCollectionRuleDataSources,
    KnownColumnDefinitionType, ColumnDefinition,
    LogAnalyticsDestination, DataFlow,
)
from azure.mgmt.monitor.operations import DataCollectionRulesOperations

from davidkhala.azure.monitor import AbstractResource


class DCR:
    @dataclass
    class Resource(AbstractResource):
        stream_declarations: Dict[str, StreamDeclaration] | None
        data_collection_endpoint_id: str

        def from_resource(self, resource: DataCollectionRuleResource):
            super().from_resource(resource)
            self.stream_declarations = resource.stream_declarations
            self.data_collection_endpoint_id = resource.data_collection_endpoint_id
            return self

        def get_one_stream(self) -> str | None:
            if self.stream_declarations is not None:
                for stream in self.stream_declarations.keys():
                    return stream

        def schema(self, stream_name) -> dict[str, KnownColumnDefinitionType | str]:
            r = {}
            for column in self.stream_declarations[stream_name].columns:
                r[column.name] = column.type
            return r

    class Destinations:
        def __init__(self, destinations: DataCollectionRuleDestinations):
            mapper = lambda l: [] if l is None else (item.name for item in l)

            self.names = [
                *mapper(destinations.log_analytics),
                *mapper(destinations.monitoring_accounts),
                *mapper(destinations.azure_monitor_metrics),
                *mapper(destinations.event_hubs),
                *mapper(destinations.event_hubs_direct),
                *mapper(destinations.storage_blobs_direct),
                *mapper(destinations.storage_tables_direct),
                *mapper(destinations.storage_accounts),
            ]

    def __init__(self, data_collection_rules: DataCollectionRulesOperations):
        self.data_collection_rules = data_collection_rules

    def get(self, resource_group_name: str, name: str) -> Resource:
        r = self.data_collection_rules.get(resource_group_name, name)
        return DCR.Resource(*[None] * 7).from_resource(r)

    def get_by_id(self, resource_id: str):
        words = resource_id.split("/")
        return self.get(words[4], words[-1])

    def list(self) -> Iterable[DataCollectionRuleResource]:
        return self.data_collection_rules.list_by_subscription()

    def delete(self, resource_group_name: str, name: str):
        return self.data_collection_rules.delete(resource_group_name, name)


from davidkhala.azure.monitor.log import AnalyticsWorkspace
from davidkhala.azure.monitor.dce import DCE


class Factory:
    location: str
    data_collection_endpoint_id: str

    def __init__(self,
                 resource_group_name: str,
                 name: str):

        self.resource_group_name = resource_group_name
        self.name = name
        self.stream_declarations = {}
        self.destinations = DataCollectionRuleDestinations()
        self.data_flows: List[DataFlow] = []
        self.data_sources = DataCollectionRuleDataSources()

    def with_DataCollectionEndpoint(self, dce: DCE.Resource):
        self.location = dce.location
        self.data_collection_endpoint_id = dce.id
        return self

    def with_LogAnalyticsTable(self, name, schema: dict[str, KnownColumnDefinitionType | str],
                               workspace: AnalyticsWorkspace.Resource):
        stream_name = f"Custom-{name}_CL"
        schema["TimeGenerated"] = KnownColumnDefinitionType.DATETIME  # decorate
        columns = [ColumnDefinition(name=name, type=_type) for name, _type in schema.items()]
        self.stream_declarations[stream_name] = StreamDeclaration(columns=columns)

        _workspace = LogAnalyticsDestination(
            workspace_resource_id=workspace.id,
            name=workspace.immutable_id.replace('-', ''),
        )
        _workspace.workspace_id = workspace.immutable_id

        if self.destinations.log_analytics is None:
            self.destinations.log_analytics = [_workspace]
        else:
            self.destinations.log_analytics.append(_workspace)

        self.data_flows.append(DataFlow(
            streams=[stream_name],
            destinations=[_workspace.name],
            transform_kql="source | extend TimeGenerated = now()",
            output_stream=stream_name
        ))
        return self

    def build(self, operations: DataCollectionRulesOperations):
        body = DataCollectionRuleResource(
            location=self.location,
            data_collection_endpoint_id=self.data_collection_endpoint_id,
            stream_declarations=self.stream_declarations,
            data_sources=self.data_sources,
            destinations=self.destinations,
            data_flows=self.data_flows,
        )
        return operations.create(self.resource_group_name, self.name, body)
