from __future__ import annotations

from typing import Iterable

from google.protobuf.json_format import MessageToDict, ParseDict

from glassdome_waypoint_sdk.api.external.waypoint.v1beta1 import (
    pcf_pb2,
)

from .._internal import BaseClient
from .operation import Operation
from .types.pcf import (
    Fact,
    UpdateFlowRequest,
    UpdateLinkRequest,
    UpdateUnitProcessRequest,
)


class PCFClient(BaseClient):
    """
    Client for PCF APIs (/v1beta1/sustainabilities/pcf...).
    """

    # POST /v1beta1/sustainabilities/pcf/unit_processes:batchupdate
    def update_unit_processes(
        self,
        requests: Iterable[UpdateUnitProcessRequest],
        allow_partial_success: bool = False,
    ) -> Operation:
        """
        Update unit processes as a long-running operation.

        Args:
            requests:
                Iterable of UpdateUnitProcessRequest messages.
                Each must contain:
                  - unit_process.id
                  - update_mask (for normal updates)
                and may set allow_missing for upsert behavior.
            allow_partial_success:
                Mirrors BatchUpdateUnitProcessesRequest.allow_partial_success.

        Returns:
            Operation proto from BatchUpdateUnitProcessesResponse.operation.
        """
        req = pcf_pb2.BatchUpdateUnitProcessesRequest(
            requests=requests,
            allow_partial_success=allow_partial_success,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request(
            "POST",
            "/v1beta1/sustainabilities/pcf/unit_processes:batchupdate",
            json=req_json,
        )
        resp = pcf_pb2.BatchUpdateUnitProcessesResponse()
        ParseDict(resp_json, resp)

        return Operation(self, resp.operation)

    # POST /v1beta1/sustainabilities/pcf/flows:batchupdate
    def update_flows(
        self,
        requests: Iterable[UpdateFlowRequest],
        allow_partial_success: bool = False,
    ) -> Operation:
        """
        Update flows as a long-running operation.

        Args:
            requests:
                Iterable of UpdateFlowRequest messages. Each must contain:
                  - flow.id
                  - update_mask (for normal updates)
                and may set allow_missing for upsert behavior.
            allow_partial_success:
                Mirrors BatchUpdateFlowsRequest.allow_partial_success.

        Returns:
            Operation proto from BatchUpdateFlowsResponse.operation.
        """
        req = pcf_pb2.BatchUpdateFlowsRequest(
            requests=requests,
            allow_partial_success=allow_partial_success,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request(
            "POST", "/v1beta1/sustainabilities/pcf/flows:batchupdate", json=req_json
        )
        resp = pcf_pb2.BatchUpdateFlowsResponse()
        ParseDict(resp_json, resp)

        return Operation(self, resp.operation)

    # POST /v1beta1/sustainabilities/pcf/links:batchupdate
    def update_links(
        self,
        requests: Iterable[UpdateLinkRequest],
        allow_partial_success: bool = False,
    ) -> Operation:
        """
        Update links as a long-running operation.

        Args:
            requests:
                Iterable of UpdateLinkRequest messages. Each must contain:
                  - link.unit_process_id
                  - link.component_id
                  - update_mask (for normal updates)
                and may set allow_missing for upsert behavior.
            allow_partial_success:
                Mirrors BatchUpdateLinksRequest.allow_partial_success.

        Returns:
            Operation proto from BatchUpdateLinksResponse.operation.
        """
        req = pcf_pb2.BatchUpdateLinksRequest(
            requests=requests,
            allow_partial_success=allow_partial_success,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request(
            "POST", "/v1beta1/sustainabilities/pcf/links:batchupdate", json=req_json
        )
        resp = pcf_pb2.BatchUpdateLinksResponse()
        ParseDict(resp_json, resp)

        return Operation(self, resp.operation)

    # POST /v1beta1/sustainabilities/pcf/facts:batchinsert
    def insert_facts(
        self,
        records: Iterable[Fact],
        allow_partial_success: bool = False,
    ) -> Operation:
        """
        Insert facts as a long-running operation.

        Args:
            records:
                Iterable of Fact messages. Each must contain:
                  - month
                  - site_id
                  - unit_process_id
                  - component_id
                  - component_kind
                  - direction
                  - amount
            allow_partial_success:
                Mirrors BatchInsertFactsRequest.allow_partial_success.
        Returns:
            Operation proto from BatchInsertFactsResponse.operation.
        """
        req = pcf_pb2.BatchInsertFactsRequest(
            records=records,
            allow_partial_success=allow_partial_success,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request(
            "POST", "/v1beta1/sustainabilities/pcf/facts:batchinsert", json=req_json
        )
        resp = pcf_pb2.BatchInsertFactsResponse()
        ParseDict(resp_json, resp)

        return Operation(self, resp.operation)
