from glassdome_waypoint_sdk.api.buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DQR(_message.Message):
    __slots__ = ()
    TECHNOLOGICAL_DQR_FIELD_NUMBER: _ClassVar[int]
    TEMPORAL_DQR_FIELD_NUMBER: _ClassVar[int]
    GEOGRAPHICAL_DQR_FIELD_NUMBER: _ClassVar[int]
    technological_dqr: int
    temporal_dqr: int
    geographical_dqr: int
    def __init__(self, technological_dqr: _Optional[int] = ..., temporal_dqr: _Optional[int] = ..., geographical_dqr: _Optional[int] = ...) -> None: ...
