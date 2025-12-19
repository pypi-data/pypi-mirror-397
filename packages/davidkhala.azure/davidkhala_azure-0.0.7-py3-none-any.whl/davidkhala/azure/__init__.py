from typing import Optional, Any

from azure.core.credentials import TokenCredential as AzTokenCredential, AccessToken
from azure.identity._internal.get_token_mixin import GetTokenMixin

default_scopes = [
    'https://management.azure.com/.default'  # for Azure Resource Manager
]


class TokenCredential(AzTokenCredential):
    def __init__(self, credential: GetTokenMixin):
        self.credential = credential

    def get_token(
            self,
            *scopes: str,
            claims: Optional[str] = None,
            tenant_id: Optional[str] = None,
            enable_cae: bool = False,
            **kwargs: Any,
    ) -> AccessToken:
        if not scopes:
            scopes = default_scopes
        return self.credential.get_token(
            *scopes,
            claims=claims, tenant_id=tenant_id, enable_cae=enable_cae,
            **kwargs)

    def __getattr__(self, item):
        # Delegate unknown attributes/methods to the wrapped instance
        return getattr(self.credential, item)
