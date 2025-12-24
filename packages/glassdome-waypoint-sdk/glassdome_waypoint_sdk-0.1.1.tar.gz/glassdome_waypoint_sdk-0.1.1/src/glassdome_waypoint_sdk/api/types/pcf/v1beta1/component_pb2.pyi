from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Component(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMPONENT_UNSPECIFIED: _ClassVar[Component]
    COMPONENT_FLOW: _ClassVar[Component]
    COMPONENT_PRODUCT: _ClassVar[Component]
COMPONENT_UNSPECIFIED: Component
COMPONENT_FLOW: Component
COMPONENT_PRODUCT: Component
