from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Stage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STAGE_UNSPECIFIED: _ClassVar[Stage]
    STAGE_PRE_MANUFACTURING: _ClassVar[Stage]
    STAGE_MANUFACTURING: _ClassVar[Stage]
    STAGE_TRANSPORTATION: _ClassVar[Stage]
STAGE_UNSPECIFIED: Stage
STAGE_PRE_MANUFACTURING: Stage
STAGE_MANUFACTURING: Stage
STAGE_TRANSPORTATION: Stage
