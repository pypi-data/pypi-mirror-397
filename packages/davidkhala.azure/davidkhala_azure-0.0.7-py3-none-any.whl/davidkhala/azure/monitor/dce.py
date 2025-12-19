from dataclasses import dataclass
from typing import Iterable

from azure.mgmt.monitor.models import (
    DataCollectionEndpointResource, DataCollectionEndpointNetworkAcls, KnownPublicNetworkAccessOptions
)
from azure.mgmt.monitor.operations import DataCollectionEndpointsOperations

from davidkhala.azure.monitor import AbstractResource


class DCE:
    def __init__(self, data_collection_endpoints: DataCollectionEndpointsOperations):
        self.data_collection_endpoints = data_collection_endpoints

    @dataclass
    class Resource(AbstractResource):
        configuration_access: str
        logs_ingestion: str

        def from_resource(self, r: DataCollectionEndpointResource):
            super().from_resource(r)
            self.configuration_access = r.configuration_access.endpoint
            self.logs_ingestion = r.logs_ingestion.endpoint
            return self

    def create(self, resource_group_name, name, location="East Asia") -> Resource:
        body = DataCollectionEndpointResource(
            location=location,
            network_acls=DataCollectionEndpointNetworkAcls(
                public_network_access=KnownPublicNetworkAccessOptions.ENABLED
            )
        )
        return DCE.Resource(*[None] * 7).from_resource(
            self.data_collection_endpoints.create(resource_group_name, name, body)
        )

    def get(self, resource_group_name, name) -> Resource:
        return DCE.Resource(*[None] * 7).from_resource(
            self.data_collection_endpoints.get(resource_group_name, name)
        )

    def get_by_id(self, resource_id: str):
        words = resource_id.split("/")
        return self.get(words[4], words[-1])

    def delete(self, resource_group_name: str, name: str):
        self.data_collection_endpoints.delete(resource_group_name, name)

    def list(self) -> Iterable[DataCollectionEndpointResource]:
        return self.data_collection_endpoints.list_by_subscription()
