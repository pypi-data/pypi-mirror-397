from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_UNSPECIFIED: _ClassVar[Status]
    STATUS_ACTIVE: _ClassVar[Status]
    STATUS_INACTIVE: _ClassVar[Status]
STATUS_UNSPECIFIED: Status
STATUS_ACTIVE: Status
STATUS_INACTIVE: Status
