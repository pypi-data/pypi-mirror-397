import os

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential

from davidkhala.azure.auth import from_service_principal, default


def credentials() -> TokenCredential | DefaultAzureCredential:
    client_secret = os.environ.get('CLIENT_SECRET')
    if client_secret:
        return from_service_principal(
            tenant_id=os.environ.get('TENANT_ID'),
            client_id=os.environ.get('CLIENT_ID'),
            client_secret=client_secret,
        )
    return default()
