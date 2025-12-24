from __future__ import annotations

from google.protobuf.json_format import MessageToDict, ParseDict

from glassdome_waypoint_sdk.api.external.waypoint.v1beta1 import site_pb2

from .._internal import BaseClient
from .types.site import Site


class SiteClient(BaseClient):
    """
    Client for Site APIs (/v1beta1/sites...).
    """

    # GET /v1beta1/sites
    def list_sites(
        self,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> tuple[list[Site], str]:
        req = site_pb2.ListSitesRequest(
            page_size=page_size,
            page_token=page_token,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request("GET", "/v1beta1/sites", params=req_json)
        resp = site_pb2.ListSitesResponse()
        ParseDict(resp_json, resp)

        return list(resp.sites), resp.next_page_token
