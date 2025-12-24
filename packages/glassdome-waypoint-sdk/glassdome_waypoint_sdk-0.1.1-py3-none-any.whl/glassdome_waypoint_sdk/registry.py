from __future__ import annotations

from google.protobuf.any_pb2 import Any
from google.protobuf.message import Message

from . import AnyUnpackError, Error
from .v1beta1.types.pcf import (
    BatchInsertFactsOperationResponse as v1beta1_BatchInsertFactsOperationResponse,
)
from .v1beta1.types.pcf import (
    BatchUpdateFlowsOperationResponse as v1beta1_BatchUpdateFlowsOperationResponse,
)
from .v1beta1.types.pcf import (
    BatchUpdateLinksOperationResponse as v1beta1_BatchUpdateLinksOperationResponse,
)
from .v1beta1.types.pcf import (
    BatchUpdateUnitProcessesOperationResponse as v1beta1_BatchUpdateUnitProcessesOperationResponse,
)
from .v1beta1.types.product import (
    BatchCreateProductsOperationResponse as v1beta1_BatchCreateProductsOperationResponse,
)
from .v1beta1.types.product import (
    BatchDeleteProductsOperationResponse as v1beta1_BatchDeleteProductsOperationResponse,
)
from .v1beta1.types.product import (
    BatchUpdateProductsOperationResponse as v1beta1_BatchUpdateProductsOperationResponse,
)


def _versioned_name_from_full_name(full_name: str) -> str:
    splits = full_name.split(".")
    if len(splits) < 2:
        return full_name

    return f"{splits[-2]}.{splits[-1]}"


class AnyRegistry:
    """
    Global registry for mapping any_pb2.Any -> concrete protobuf message.

    Usage:
        msg = AnyRegistry.unpack(any_msg)
    """

    _type_map: dict[str, type[Message]] = {
        _versioned_name_from_full_name(Error.DESCRIPTOR.full_name): Error,
        _versioned_name_from_full_name(
            v1beta1_BatchCreateProductsOperationResponse.DESCRIPTOR.full_name
        ): v1beta1_BatchCreateProductsOperationResponse,
        _versioned_name_from_full_name(
            v1beta1_BatchDeleteProductsOperationResponse.DESCRIPTOR.full_name
        ): v1beta1_BatchDeleteProductsOperationResponse,
        _versioned_name_from_full_name(
            v1beta1_BatchUpdateProductsOperationResponse.DESCRIPTOR.full_name
        ): v1beta1_BatchUpdateProductsOperationResponse,
        _versioned_name_from_full_name(
            v1beta1_BatchUpdateUnitProcessesOperationResponse.DESCRIPTOR.full_name
        ): v1beta1_BatchUpdateUnitProcessesOperationResponse,
        _versioned_name_from_full_name(
            v1beta1_BatchUpdateFlowsOperationResponse.DESCRIPTOR.full_name
        ): v1beta1_BatchUpdateFlowsOperationResponse,
        _versioned_name_from_full_name(
            v1beta1_BatchUpdateLinksOperationResponse.DESCRIPTOR.full_name
        ): v1beta1_BatchUpdateLinksOperationResponse,
        _versioned_name_from_full_name(
            v1beta1_BatchInsertFactsOperationResponse.DESCRIPTOR.full_name
        ): v1beta1_BatchInsertFactsOperationResponse,
    }

    @classmethod
    def unpack(cls, any_msg: Any) -> Message:
        versioned_name = cls._versioned_name_from_type_url(any_msg.type_url)
        try:
            msg_type = cls._type_map[versioned_name]
        except KeyError as e:
            raise AnyUnpackError(
                f"Unknown Any message type for type_url={any_msg.type_url!r}, "
                f"derived key={versioned_name!r}"
            ) from e

        msg = msg_type()
        any_msg.Unpack(msg)

        return msg

    @classmethod
    def _versioned_name_from_type_url(cls, type_url: str) -> str:
        full_name = type_url.split("/")[-1]
        return _versioned_name_from_full_name(full_name)
