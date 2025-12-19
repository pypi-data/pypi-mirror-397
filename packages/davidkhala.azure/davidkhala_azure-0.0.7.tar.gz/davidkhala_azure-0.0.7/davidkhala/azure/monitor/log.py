from dataclasses import dataclass
from typing import Iterable, Iterator

from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.mgmt.loganalytics.models import Table, Workspace as NativeWorkspace
from azure.mgmt.loganalytics.operations import TablesOperations

from davidkhala.azure import TokenCredential
from davidkhala.azure.monitor import AbstractResource


class AnalyticsWorkspace:
    def __init__(self, credential: TokenCredential, subscription_id: str):
        self.client = LogAnalyticsManagementClient(credential, subscription_id)

    def list(self) -> Iterable[NativeWorkspace]:
        return self.client.workspaces.list()

    @dataclass
    class Resource(AbstractResource):

        def __init__(self, operations: TablesOperations):
            super().__init__(*[None] * 5)
            self.operations = operations

        def from_resource(self, resource: NativeWorkspace):
            super().from_resource(resource)
            self.immutable_id = resource.customer_id
            return self

    def create(self, resource_group_name, name) -> Resource:
        promise = self.client.workspaces.begin_create_or_update(resource_group_name, name)
        return AnalyticsWorkspace.Resource(self.tables).from_resource(promise.result())

    @property
    def tables(self) -> TablesOperations:
        return self.client.tables

    def delete(self, resource_group_name: str, name: str, force=True):
        """
        :param name:
        :param resource_group_name:
        :param force: Deletes the workspace without the recovery option (kept for 14 days).
        """
        promise = self.client.workspaces.begin_delete(resource_group_name, name, force)
        promise.result()

    def get(self, resource_group_name, name) -> Resource:
        resource = self.client.workspaces.get(resource_group_name, name)
        return AnalyticsWorkspace.Resource(self.tables).from_resource(resource)


class AnalyticsTable:
    def __init__(self, workspace: AnalyticsWorkspace.Resource):
        self.tables = workspace.operations
        self.workspace = workspace.name
        self.resource_group_name = workspace.resource_group_name

    def list(self, *, no_system: bool = False) -> Iterator[Table]:
        for table in self.tables.list_by_workspace(self.resource_group_name, self.workspace):
            if no_system and not str(table.name).endswith('_CL'):
                continue
            yield table

    def create(self, table_name: str) -> Table:
        parameters = Table()
        promise = self.tables.begin_create_or_update(self.resource_group_name, self.workspace, table_name, parameters)
        return promise.result()
