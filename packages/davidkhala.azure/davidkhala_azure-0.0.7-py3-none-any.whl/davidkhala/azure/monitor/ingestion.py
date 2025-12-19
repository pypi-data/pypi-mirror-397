from typing import List

from azure.identity import ClientSecretCredential
from azure.mgmt.loganalytics.models import ColumnTypeEnum
from azure.monitor.ingestion import LogsIngestionClient

from davidkhala.azure import TokenCredential
from davidkhala.azure.monitor.dce import DCE
from davidkhala.azure.monitor.dcr import DCR


class Ingestion:
    logs: List[dict]
    stream_name: str
    dcr: DCR.Resource
    schema: dict[str, ColumnTypeEnum | str]

    def __init__(self, credential: TokenCredential, dcr: DCR.Resource, end_point: str | None,
                 *,
                 dce_operations: DCE = None):
        assert type(credential.credential) == ClientSecretCredential
        if end_point is None:
            end_point = dce_operations.get_by_id(dcr.data_collection_endpoint_id).logs_ingestion
        """
        The Data Collection Endpoint for the Data Collection Rule (e.g. https://dce-name.eastus-2.ingest.monitor.azure.com.)
        """
        self.dcr = dcr
        self.client = LogsIngestionClient(end_point, credential)

    def getLogger(self, stream_name: str = None):
        if stream_name is None:
            stream_name = self.dcr.get_one_stream()
        assert stream_name is not None
        self.stream_name = stream_name
        self.schema = self.dcr.schema(stream_name)
        del self.schema['TimeGenerated']
        self.logs = []
        return self

    def commit(self):
        self.client.upload(self.dcr.immutable_id, self.stream_name, self.logs)

    def log(self, message: dict):
        assert message.keys() == self.schema.keys()
        self.logs.append(message)
