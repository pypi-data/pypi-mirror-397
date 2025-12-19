import json
import subprocess
from typing import Iterator, Tuple, TypedDict

from azure.core.credentials import TokenProvider
from azure.identity import (
    DefaultAzureCredential, AzureCliCredential,
    EnvironmentCredential, ManagedIdentityCredential, SharedTokenCacheCredential,
    AzurePowerShellCredential, AzureDeveloperCliCredential, ClientSecretCredential,
)
from davidkhala.utils.syntax.env import is_windows, is_mac, is_linux

from davidkhala.azure import TokenCredential, default_scopes

DefaultCredentialType = EnvironmentCredential | ManagedIdentityCredential | SharedTokenCacheCredential | AzureCliCredential | AzurePowerShellCredential | AzureDeveloperCliCredential
default = DefaultAzureCredential


def from_service_principal(tenant_id: str, client_id: str, client_secret: str) -> TokenCredential:
    return TokenCredential(ClientSecretCredential(tenant_id, client_id, client_secret))


from azure.identity import CredentialUnavailableError


class CliCredential:
    class Structure(TypedDict):
        class User(TypedDict):
            name: str
            type: str

        class Tenant(TypedDict):
            tenantId: str

        environmentName: str
        homeTenantId: str
        id: str
        isDefault: bool
        managedByTenants: list[Tenant]
        name: str
        state: str
        tenantId: str
        user: User

    @staticmethod
    def current():
        command = None
        if is_windows():
            command = 'az.cmd'
        elif is_linux():
            command = '/usr/bin/az'
        elif is_mac():
            # TODO
            ...

        r = subprocess.run([command, 'account', 'show'], capture_output=True, text=True)
        data = r.stdout.strip()
        return CliCredential.Structure(**json.loads(data))


def actually(credentials: DefaultAzureCredential) -> Iterator[Tuple[TokenProvider, int]]:
    """
    Personal Microsoft account is not supported to get_token(...)
    :param credentials:
    :return:
    """
    for i, credential in enumerate(credentials.credentials):
        try:
            credential.get_token(*default_scopes)
            yield credential, i
        except CredentialUnavailableError as na_error:
            err_str = str(na_error)

            swallow: bool = False
            match i:
                case 0:
                    swallow = err_str == """EnvironmentCredential authentication unavailable. Environment variables are not fully configured.
Visit https://aka.ms/azsdk/python/identity/environmentcredential/troubleshoot to troubleshoot this issue."""
                case 1:
                    swallow = err_str in [
                        'ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint.',
                        'ManagedIdentityCredential authentication unavailable, no response from the IMDS endpoint. invalid_request'
                    ]
                case 2:
                    swallow = err_str == 'SharedTokenCacheCredential authentication unavailable. No accounts were found in the cache.'
                case 3:
                    swallow = err_str == "Please run 'az login' to set up an account"
                case 4:
                    swallow = err_str in [
                        'Az.Account module >= 2.2.0 is not installed',
                        'Please run "Connect-AzAccount" to set up account'
                    ]

                case 5:
                    swallow = err_str in [
                        "Azure Developer CLI could not be found. Please visit https://aka.ms/azure-dev for installation instructions and then,once installed, authenticate to your Azure account using 'azd auth login'.",
                        "Please run 'azd auth login' from a command prompt to authenticate before using this credential."
                    ]
            if not swallow:
                raise na_error
