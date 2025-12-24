from glassdome_waypoint_sdk.api.buf.validate import validate_pb2 as _validate_pb2
from glassdome_waypoint_sdk.api.external.waypoint.v1beta1 import operation_pb2 as _operation_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from glassdome_waypoint_sdk.api.protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from glassdome_waypoint_sdk.api.types.product.v1beta1 import status_pb2 as _status_pb2
from glassdome_waypoint_sdk.api.types.unit.v1beta1 import unit_of_measure_pb2 as _unit_of_measure_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Product(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_IDS_FIELD_NUMBER: _ClassVar[int]
    SKU_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    UOM_FIELD_NUMBER: _ClassVar[int]
    SITE_IDS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    group_ids: _containers.RepeatedScalarFieldContainer[str]
    sku: str
    status: _status_pb2.Status
    uom: _unit_of_measure_pb2.UnitOfMeasure
    site_ids: _containers.RepeatedScalarFieldContainer[str]
    description: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., group_ids: _Optional[_Iterable[str]] = ..., sku: _Optional[str] = ..., status: _Optional[_Union[_status_pb2.Status, str]] = ..., uom: _Optional[_Union[_unit_of_measure_pb2.UnitOfMeasure, str]] = ..., site_ids: _Optional[_Iterable[str]] = ..., description: _Optional[str] = ...) -> None: ...

class GetProductRequest(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetProductResponse(_message.Message):
    __slots__ = ()
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class ListProductsRequest(_message.Message):
    __slots__ = ()
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListProductsResponse(_message.Message):
    __slots__ = ()
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    next_page_token: str
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class CreateProductRequest(_message.Message):
    __slots__ = ()
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class CreateProductResponse(_message.Message):
    __slots__ = ()
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class BatchCreateProductsRequest(_message.Message):
    __slots__ = ()
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[CreateProductRequest]
    allow_partial_success: bool
    def __init__(self, requests: _Optional[_Iterable[_Union[CreateProductRequest, _Mapping]]] = ..., allow_partial_success: _Optional[bool] = ...) -> None: ...

class BatchCreateProductsResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: _operation_pb2.Operation
    def __init__(self, operation: _Optional[_Union[_operation_pb2.Operation, _Mapping]] = ...) -> None: ...

class BatchCreateProductsOperationResponse(_message.Message):
    __slots__ = ()
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ...) -> None: ...

class UpdateProductRequest(_message.Message):
    __slots__ = ()
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    ALLOW_MISSING_FIELD_NUMBER: _ClassVar[int]
    product: Product
    update_mask: _field_mask_pb2.FieldMask
    allow_missing: bool
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., allow_missing: _Optional[bool] = ...) -> None: ...

class UpdateProductResponse(_message.Message):
    __slots__ = ()
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class BatchUpdateProductsRequest(_message.Message):
    __slots__ = ()
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[UpdateProductRequest]
    allow_partial_success: bool
    def __init__(self, requests: _Optional[_Iterable[_Union[UpdateProductRequest, _Mapping]]] = ..., allow_partial_success: _Optional[bool] = ...) -> None: ...

class BatchUpdateProductsResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: _operation_pb2.Operation
    def __init__(self, operation: _Optional[_Union[_operation_pb2.Operation, _Mapping]] = ...) -> None: ...

class BatchUpdateProductsOperationResponse(_message.Message):
    __slots__ = ()
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ...) -> None: ...

class DeleteProductRequest(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    ALLOW_MISSING_FIELD_NUMBER: _ClassVar[int]
    id: str
    allow_missing: bool
    def __init__(self, id: _Optional[str] = ..., allow_missing: _Optional[bool] = ...) -> None: ...

class DeleteProductResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UndeleteProductRequest(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class UndeleteProductResponse(_message.Message):
    __slots__ = ()
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: Product
    def __init__(self, product: _Optional[_Union[Product, _Mapping]] = ...) -> None: ...

class BatchDeleteProductsRequest(_message.Message):
    __slots__ = ()
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[DeleteProductRequest]
    allow_partial_success: bool
    def __init__(self, requests: _Optional[_Iterable[_Union[DeleteProductRequest, _Mapping]]] = ..., allow_partial_success: _Optional[bool] = ...) -> None: ...

class BatchDeleteProductsResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: _operation_pb2.Operation
    def __init__(self, operation: _Optional[_Union[_operation_pb2.Operation, _Mapping]] = ...) -> None: ...

class BatchDeleteProductsOperationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BatchUndeleteProductsRequest(_message.Message):
    __slots__ = ()
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[UndeleteProductRequest]
    allow_partial_success: bool
    def __init__(self, requests: _Optional[_Iterable[_Union[UndeleteProductRequest, _Mapping]]] = ..., allow_partial_success: _Optional[bool] = ...) -> None: ...

class BatchUndeleteProductsResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: _operation_pb2.Operation
    def __init__(self, operation: _Optional[_Union[_operation_pb2.Operation, _Mapping]] = ...) -> None: ...

class BatchUndeleteProductsOperationResponse(_message.Message):
    __slots__ = ()
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ...) -> None: ...

class ProductGroup(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_IDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    product_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., product_ids: _Optional[_Iterable[str]] = ...) -> None: ...
