from __future__ import annotations

from typing import Iterable

from google.protobuf.json_format import MessageToDict, ParseDict

from glassdome_waypoint_sdk.api.external.waypoint.v1beta1 import (
    product_pb2,
)

from .._internal import BaseClient
from .operation import Operation
from .types.product import (
    CreateProductRequest,
    DeleteProductRequest,
    UpdateProductRequest,
)


class ProductClient(BaseClient):
    """
    Client for Product APIs (/v1beta1/products...).
    """

    # POST /v1beta1/products:batchcreate
    def create_products(
        self,
        requests: Iterable[CreateProductRequest],
        allow_partial_success: bool = False,
    ) -> Operation:
        """
        Create products as a long-running operation.

        Args:
            requests:
                Iterable of CreateProductRequest messages.
                Each must contain the required fields for a product.
            allow_partial_success:
                Mirrors BatchCreateProductsRequest.allow_partial_success.

        Returns:
            Operation proto from BatchCreateProductsResponse.operation.
        """
        req = product_pb2.BatchCreateProductsRequest(
            requests=requests,
            allow_partial_success=allow_partial_success,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request(
            "POST", "/v1beta1/products:batchcreate", json=req_json
        )
        resp = product_pb2.BatchCreateProductsResponse()
        ParseDict(resp_json, resp)

        return Operation(self, resp.operation)

    # POST /v1beta1/products:batchupdate
    def update_products(
        self,
        requests: Iterable[UpdateProductRequest],
        allow_partial_success: bool = False,
    ) -> Operation:
        """
        Update products as a long-running operation.

        Args:
            requests:
                Iterable of UpdateProductRequest messages. Each must contain:
                  - product.id
                  - update_mask (for normal updates)
                and may set allow_missing for upsert behavior.
            allow_partial_success:
                Mirrors BatchUpdateProductsRequest.allow_partial_success.

        Returns:
            Operation proto from BatchUpdateProductsResponse.operation.
        """
        req = product_pb2.BatchUpdateProductsRequest(
            requests=requests,
            allow_partial_success=allow_partial_success,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request(
            "POST", "/v1beta1/products:batchupdate", json=req_json
        )
        resp = product_pb2.BatchUpdateProductsResponse()
        ParseDict(resp_json, resp)

        return Operation(self, resp.operation)

    # POST /v1beta1/products:batchdelete
    def delete_products(
        self,
        requests: Iterable[DeleteProductRequest],
        allow_partial_success: bool = False,
    ) -> Operation:
        """
        Delete products as a long-running operation.

        Args:
            requests:
                Iterable of DeleteProductRequest messages.
                Each must contain the product id; may set allow_missing.
            allow_partial_success:
                Mirrors BatchDeleteProductsRequest.allow_partial_success.

        Returns:
            Operation proto from BatchDeleteProductsResponse.operation.
        """
        req = product_pb2.BatchDeleteProductsRequest(
            requests=requests,
            allow_partial_success=allow_partial_success,
        )
        req_json = MessageToDict(req, preserving_proto_field_name=True)

        resp_json = self._request(
            "POST", "/v1beta1/products:batchdelete", json=req_json
        )
        resp = product_pb2.BatchDeleteProductsResponse()
        ParseDict(resp_json, resp)

        return Operation(self, resp.operation)
