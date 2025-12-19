from typing import Iterable

from azure.core.credentials import TokenCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource.subscriptions.models import Subscription as NativeSubscription


class Subscription:
    def __init__(self, credential: TokenCredential):
        self.client = SubscriptionClient(credential)

    def list(self) -> Iterable[NativeSubscription]:
        return self.client.subscriptions.list()

    def get(self, subscription_id: str) -> NativeSubscription:
        return self.client.subscriptions.get(subscription_id)

    def get_one(self) -> NativeSubscription:
        return next(iter(self.list()))

