from glassdome_waypoint_sdk.api.buf.validate import validate_pb2 as _validate_pb2
from glassdome_waypoint_sdk.api.external.waypoint.v1beta1 import operation_pb2 as _operation_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from glassdome_waypoint_sdk.api.protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from glassdome_waypoint_sdk.api.types.pcf.v1beta1 import category_pb2 as _category_pb2
from glassdome_waypoint_sdk.api.types.pcf.v1beta1 import component_pb2 as _component_pb2
from glassdome_waypoint_sdk.api.types.pcf.v1beta1 import direction_pb2 as _direction_pb2
from glassdome_waypoint_sdk.api.types.pcf.v1beta1 import dqr_pb2 as _dqr_pb2
from glassdome_waypoint_sdk.api.types.pcf.v1beta1 import stage_pb2 as _stage_pb2
from glassdome_waypoint_sdk.api.types.unit.v1beta1 import unit_of_measure_pb2 as _unit_of_measure_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnitProcess(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    SITE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    site_id: str
    name: str
    description: str
    def __init__(self, id: _Optional[str] = ..., site_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class UpdateUnitProcessRequest(_message.Message):
    __slots__ = ()
    UNIT_PROCESS_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    ALLOW_MISSING_FIELD_NUMBER: _ClassVar[int]
    unit_process: UnitProcess
    update_mask: _field_mask_pb2.FieldMask
    allow_missing: bool
    def __init__(self, unit_process: _Optional[_Union[UnitProcess, _Mapping]] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., allow_missing: _Optional[bool] = ...) -> None: ...

class UpdateUnitProcessResponse(_message.Message):
    __slots__ = ()
    UNIT_PROCESS_FIELD_NUMBER: _ClassVar[int]
    unit_process: UnitProcess
    def __init__(self, unit_process: _Optional[_Union[UnitProcess, _Mapping]] = ...) -> None: ...

class BatchUpdateUnitProcessesRequest(_message.Message):
    __slots__ = ()
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_ONLY_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[UpdateUnitProcessRequest]
    allow_partial_success: bool
    validate_only: bool
    def __init__(self, requests: _Optional[_Iterable[_Union[UpdateUnitProcessRequest, _Mapping]]] = ..., allow_partial_success: _Optional[bool] = ..., validate_only: _Optional[bool] = ...) -> None: ...

class BatchUpdateUnitProcessesResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: _operation_pb2.Operation
    def __init__(self, operation: _Optional[_Union[_operation_pb2.Operation, _Mapping]] = ...) -> None: ...

class BatchUpdateUnitProcessesOperationResponse(_message.Message):
    __slots__ = ()
    UNIT_PROCESSES_FIELD_NUMBER: _ClassVar[int]
    unit_processes: _containers.RepeatedCompositeFieldContainer[UnitProcess]
    def __init__(self, unit_processes: _Optional[_Iterable[_Union[UnitProcess, _Mapping]]] = ...) -> None: ...

class Flow(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    SITE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UOM_FIELD_NUMBER: _ClassVar[int]
    IN_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    OUT_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    DQR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    site_id: str
    name: str
    uom: _unit_of_measure_pb2.UnitOfMeasure
    in_category: _category_pb2.InCategory
    out_category: _category_pb2.OutCategory
    stage: _stage_pb2.Stage
    dqr: _dqr_pb2.DQR
    description: str
    def __init__(self, id: _Optional[str] = ..., site_id: _Optional[str] = ..., name: _Optional[str] = ..., uom: _Optional[_Union[_unit_of_measure_pb2.UnitOfMeasure, str]] = ..., in_category: _Optional[_Union[_category_pb2.InCategory, str]] = ..., out_category: _Optional[_Union[_category_pb2.OutCategory, str]] = ..., stage: _Optional[_Union[_stage_pb2.Stage, str]] = ..., dqr: _Optional[_Union[_dqr_pb2.DQR, _Mapping]] = ..., description: _Optional[str] = ...) -> None: ...

class UpdateFlowRequest(_message.Message):
    __slots__ = ()
    FLOW_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    ALLOW_MISSING_FIELD_NUMBER: _ClassVar[int]
    flow: Flow
    update_mask: _field_mask_pb2.FieldMask
    allow_missing: bool
    def __init__(self, flow: _Optional[_Union[Flow, _Mapping]] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., allow_missing: _Optional[bool] = ...) -> None: ...

class UpdateFlowResponse(_message.Message):
    __slots__ = ()
    FLOW_FIELD_NUMBER: _ClassVar[int]
    flow: Flow
    def __init__(self, flow: _Optional[_Union[Flow, _Mapping]] = ...) -> None: ...

class BatchUpdateFlowsRequest(_message.Message):
    __slots__ = ()
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_ONLY_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[UpdateFlowRequest]
    allow_partial_success: bool
    validate_only: bool
    def __init__(self, requests: _Optional[_Iterable[_Union[UpdateFlowRequest, _Mapping]]] = ..., allow_partial_success: _Optional[bool] = ..., validate_only: _Optional[bool] = ...) -> None: ...

class BatchUpdateFlowsResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: _operation_pb2.Operation
    def __init__(self, operation: _Optional[_Union[_operation_pb2.Operation, _Mapping]] = ...) -> None: ...

class BatchUpdateFlowsOperationResponse(_message.Message):
    __slots__ = ()
    FLOWS_FIELD_NUMBER: _ClassVar[int]
    flows: _containers.RepeatedCompositeFieldContainer[Flow]
    def __init__(self, flows: _Optional[_Iterable[_Union[Flow, _Mapping]]] = ...) -> None: ...

class Link(_message.Message):
    __slots__ = ()
    UNIT_PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_KIND_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    unit_process_id: str
    component_id: str
    component_kind: _component_pb2.Component
    direction: _direction_pb2.Direction
    def __init__(self, unit_process_id: _Optional[str] = ..., component_id: _Optional[str] = ..., component_kind: _Optional[_Union[_component_pb2.Component, str]] = ..., direction: _Optional[_Union[_direction_pb2.Direction, str]] = ...) -> None: ...

class UpdateLinkRequest(_message.Message):
    __slots__ = ()
    LINK_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    ALLOW_MISSING_FIELD_NUMBER: _ClassVar[int]
    link: Link
    update_mask: _field_mask_pb2.FieldMask
    allow_missing: bool
    def __init__(self, link: _Optional[_Union[Link, _Mapping]] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ..., allow_missing: _Optional[bool] = ...) -> None: ...

class UpdateLinkResponse(_message.Message):
    __slots__ = ()
    LINK_FIELD_NUMBER: _ClassVar[int]
    link: Link
    def __init__(self, link: _Optional[_Union[Link, _Mapping]] = ...) -> None: ...

class BatchUpdateLinksRequest(_message.Message):
    __slots__ = ()
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_ONLY_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[UpdateLinkRequest]
    allow_partial_success: bool
    validate_only: bool
    def __init__(self, requests: _Optional[_Iterable[_Union[UpdateLinkRequest, _Mapping]]] = ..., allow_partial_success: _Optional[bool] = ..., validate_only: _Optional[bool] = ...) -> None: ...

class BatchUpdateLinksResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: _operation_pb2.Operation
    def __init__(self, operation: _Optional[_Union[_operation_pb2.Operation, _Mapping]] = ...) -> None: ...

class BatchUpdateLinksOperationResponse(_message.Message):
    __slots__ = ()
    LINKS_FIELD_NUMBER: _ClassVar[int]
    links: _containers.RepeatedCompositeFieldContainer[Link]
    def __init__(self, links: _Optional[_Iterable[_Union[Link, _Mapping]]] = ...) -> None: ...

class Fact(_message.Message):
    __slots__ = ()
    MONTH_FIELD_NUMBER: _ClassVar[int]
    SITE_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_PROCESS_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_KIND_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    month: str
    site_id: str
    unit_process_id: str
    component_id: str
    component_kind: _component_pb2.Component
    direction: _direction_pb2.Direction
    amount: float
    def __init__(self, month: _Optional[str] = ..., site_id: _Optional[str] = ..., unit_process_id: _Optional[str] = ..., component_id: _Optional[str] = ..., component_kind: _Optional[_Union[_component_pb2.Component, str]] = ..., direction: _Optional[_Union[_direction_pb2.Direction, str]] = ..., amount: _Optional[float] = ...) -> None: ...

class BatchInsertFactsRequest(_message.Message):
    __slots__ = ()
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_ONLY_FIELD_NUMBER: _ClassVar[int]
    records: _containers.RepeatedCompositeFieldContainer[Fact]
    allow_partial_success: bool
    validate_only: bool
    def __init__(self, records: _Optional[_Iterable[_Union[Fact, _Mapping]]] = ..., allow_partial_success: _Optional[bool] = ..., validate_only: _Optional[bool] = ...) -> None: ...

class BatchInsertFactsResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: _operation_pb2.Operation
    def __init__(self, operation: _Optional[_Union[_operation_pb2.Operation, _Mapping]] = ...) -> None: ...

class BatchInsertFactsOperationResponse(_message.Message):
    __slots__ = ()
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    records: _containers.RepeatedCompositeFieldContainer[Fact]
    def __init__(self, records: _Optional[_Iterable[_Union[Fact, _Mapping]]] = ...) -> None: ...
