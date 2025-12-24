from __future__ import annotations

import requests

from .._internal import ApiKeyAuth, AuthBase, WaypointConfig
from .operation import OperationClient
from .pcf import PCFClient
from .product import ProductClient
from .site import SiteClient


class WaypointClient:
    def __init__(self, config: WaypointConfig, auth: AuthBase):
        session = requests.Session()
        self.operation = OperationClient(config, auth, session)
        self.site = SiteClient(config, auth, session)
        self.product = ProductClient(config, auth, session)
        self.pcf = PCFClient(config, auth, session)

    @classmethod
    def from_api_key(cls, config: WaypointConfig, api_key: str) -> WaypointClient:
        return cls(config, ApiKeyAuth(api_key=api_key))
