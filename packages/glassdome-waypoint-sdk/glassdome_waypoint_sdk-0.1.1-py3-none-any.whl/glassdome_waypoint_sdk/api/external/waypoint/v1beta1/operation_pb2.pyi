import datetime

from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.rpc import status_pb2 as _status_pb2
from glassdome_waypoint_sdk.api.protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Operation(_message.Message):
    __slots__ = ()
    class Request(_message.Message):
        __slots__ = ()
        TYPE_FIELD_NUMBER: _ClassVar[int]
        VERSION_FIELD_NUMBER: _ClassVar[int]
        NAME_FIELD_NUMBER: _ClassVar[int]
        type: str
        version: str
        name: str
        def __init__(self, type: _Optional[str] = ..., version: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...
    class Response(_message.Message):
        __slots__ = ()
        class Part(_message.Message):
            __slots__ = ()
            START_FIELD_NUMBER: _ClassVar[int]
            DATA_FIELD_NUMBER: _ClassVar[int]
            start: int
            data: _any_pb2.Any
            def __init__(self, start: _Optional[int] = ..., data: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
        PARTS_FIELD_NUMBER: _ClassVar[int]
        parts: _containers.RepeatedCompositeFieldContainer[Operation.Response.Part]
        def __init__(self, parts: _Optional[_Iterable[_Union[Operation.Response.Part, _Mapping]]] = ...) -> None: ...
    class FailedRequestsEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: _status_pb2.Status
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    COMPLETE_TIME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REQUEST_COUNT_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_REQUEST_COUNT_FIELD_NUMBER: _ClassVar[int]
    FAILED_REQUEST_COUNT_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PARTIAL_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILED_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    name: str
    done: bool
    create_time: _timestamp_pb2.Timestamp
    complete_time: _timestamp_pb2.Timestamp
    request: Operation.Request
    total_request_count: int
    successful_request_count: int
    failed_request_count: int
    allow_partial_success: bool
    failed_requests: _containers.MessageMap[int, _status_pb2.Status]
    error: _status_pb2.Status
    response: Operation.Response
    def __init__(self, name: _Optional[str] = ..., done: _Optional[bool] = ..., create_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., complete_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., request: _Optional[_Union[Operation.Request, _Mapping]] = ..., total_request_count: _Optional[int] = ..., successful_request_count: _Optional[int] = ..., failed_request_count: _Optional[int] = ..., allow_partial_success: _Optional[bool] = ..., failed_requests: _Optional[_Mapping[int, _status_pb2.Status]] = ..., error: _Optional[_Union[_status_pb2.Status, _Mapping]] = ..., response: _Optional[_Union[Operation.Response, _Mapping]] = ...) -> None: ...

class OperationReturnOptions(_message.Message):
    __slots__ = ()
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    FAILED_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    response: bool
    failed_requests: bool
    def __init__(self, response: _Optional[bool] = ..., failed_requests: _Optional[bool] = ...) -> None: ...

class GetOperationRequest(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    RETURN_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    return_options: OperationReturnOptions
    def __init__(self, id: _Optional[str] = ..., return_options: _Optional[_Union[OperationReturnOptions, _Mapping]] = ...) -> None: ...

class GetOperationResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: Operation
    def __init__(self, operation: _Optional[_Union[Operation, _Mapping]] = ...) -> None: ...

class ListOperationsRequest(_message.Message):
    __slots__ = ()
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    RETURN_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    return_options: OperationReturnOptions
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ..., return_options: _Optional[_Union[OperationReturnOptions, _Mapping]] = ...) -> None: ...

class ListOperationsResponse(_message.Message):
    __slots__ = ()
    OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    operations: _containers.RepeatedCompositeFieldContainer[Operation]
    next_page_token: str
    def __init__(self, operations: _Optional[_Iterable[_Union[Operation, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class DeleteOperationRequest(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteOperationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CancelOperationRequest(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class CancelOperationResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WaitOperationRequest(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    id: str
    timeout: _duration_pb2.Duration
    def __init__(self, id: _Optional[str] = ..., timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class WaitOperationResponse(_message.Message):
    __slots__ = ()
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    operation: Operation
    def __init__(self, operation: _Optional[_Union[Operation, _Mapping]] = ...) -> None: ...
