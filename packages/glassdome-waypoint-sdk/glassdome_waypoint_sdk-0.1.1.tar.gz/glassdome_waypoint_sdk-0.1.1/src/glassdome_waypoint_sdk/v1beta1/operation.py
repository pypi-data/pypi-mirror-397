from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google.protobuf.json_format import MessageToDict, ParseDict
from google.rpc import status_pb2

from glassdome_waypoint_sdk.api.external.waypoint.v1beta1 import operation_pb2

from .._internal import BaseClient, ExponentialBackoff, WaypointHTTPError
from .types.operation import OperationReturnOptions


def _to_params(return_options: OperationReturnOptions | None) -> dict[str, Any]:
    params: dict[str, bool] = {}
    if return_options:
        if return_options.response:
            params["return_options.response"] = True
        if return_options.failed_requests:
            params["return_options.failed_requests"] = True
    return params


@dataclass
class Operation:
    _client: BaseClient
    _op: operation_pb2.Operation
    _return_options: OperationReturnOptions | None = None

    def __getattr__(self, name: str):
        return getattr(self._op, name)

    def wait(
        self,
        exponential_backoff: ExponentialBackoff = ExponentialBackoff(),
        return_options: OperationReturnOptions | None = None,
    ) -> Operation:
        return_options = return_options or self._return_options
        for _ in exponential_backoff.sleeps():
            try:
                resp_json = self._client._request_by_url(
                    "GET", self._op.name, params=_to_params(return_options)
                )
            # If there are a number of replicas, the operation may not be available yet.
            # It should be available soon as the operation was successfully created.
            except WaypointHTTPError as e:
                if e.status_code == 404:
                    continue
                raise

            resp = operation_pb2.GetOperationResponse()
            ParseDict(resp_json, resp)

            self._op = resp.operation
            if self._op.done:
                break

        return self

    def has_error(self) -> bool:
        return self._op.done and self._op.WhichOneof("result") == "error"

    def error(self) -> status_pb2.Status | None:
        if self.has_error():
            return self._op.error
        return None

    def response(self) -> operation_pb2.Operation.Response | None:
        if self._op.done and self._op.WhichOneof("result") == "response":
            return self._op.response
        return None

    def result(self):
        return self.response() or self.error()


class OperationClient(BaseClient):
    """
    Client for Operation APIs (/v1beta1/operations...).
    """

    # GET /v1beta1/operations/{id}
    def get_operation(
        self, id: str, return_options: OperationReturnOptions | None = None
    ) -> Operation:
        resp_json = self._request(
            "GET", f"/v1beta1/operations/{id}", params=_to_params(return_options)
        )
        resp = operation_pb2.GetOperationResponse()
        ParseDict(resp_json, resp)

        return Operation(self, resp.operation, return_options)

    # GET /v1beta1/operations
    def list_operations(
        self,
        page_size: int = 100,
        page_token: str | None = None,
        return_options: OperationReturnOptions | None = None,
    ) -> tuple[list[Operation], str]:
        req = operation_pb2.ListOperationsRequest(
            page_size=page_size,
            page_token=page_token,
            return_options=return_options,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request("GET", "/v1beta1/operations", params=req_json)
        resp = operation_pb2.ListOperationsResponse()
        ParseDict(resp_json, resp)

        return [
            Operation(self, op, return_options) for op in resp.operations
        ], resp.next_page_token
