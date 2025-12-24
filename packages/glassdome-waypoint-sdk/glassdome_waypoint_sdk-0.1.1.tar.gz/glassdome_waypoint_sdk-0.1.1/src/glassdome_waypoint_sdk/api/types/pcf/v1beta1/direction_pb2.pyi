from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Direction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIRECTION_UNSPECIFIED: _ClassVar[Direction]
    DIRECTION_INPUT: _ClassVar[Direction]
    DIRECTION_OUTPUT: _ClassVar[Direction]
    DIRECTION_BIDIRECTIONAL: _ClassVar[Direction]
DIRECTION_UNSPECIFIED: Direction
DIRECTION_INPUT: Direction
DIRECTION_OUTPUT: Direction
DIRECTION_BIDIRECTIONAL: Direction
