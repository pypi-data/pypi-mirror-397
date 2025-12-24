from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class InCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IN_CATEGORY_UNSPECIFIED: _ClassVar[InCategory]
    IN_CATEGORY_RAW_MATERIAL: _ClassVar[InCategory]
    IN_CATEGORY_ANCILLARY_MATERIAL: _ClassVar[InCategory]
    IN_CATEGORY_TRANSPORTATION: _ClassVar[InCategory]
    IN_CATEGORY_PACKAGING: _ClassVar[InCategory]
    IN_CATEGORY_ENERGY: _ClassVar[InCategory]
    IN_CATEGORY_UTILITY: _ClassVar[InCategory]
    IN_CATEGORY_WIP: _ClassVar[InCategory]

class OutCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUT_CATEGORY_UNSPECIFIED: _ClassVar[OutCategory]
    OUT_CATEGORY_EMISSION_TO_AIR: _ClassVar[OutCategory]
    OUT_CATEGORY_EMISSION_TO_WATER: _ClassVar[OutCategory]
    OUT_CATEGORY_EMISSION_TO_SOIL: _ClassVar[OutCategory]
    OUT_CATEGORY_WASTE: _ClassVar[OutCategory]
    OUT_CATEGORY_TRANSPORTATION: _ClassVar[OutCategory]
    OUT_CATEGORY_SEMI_PRODUCT: _ClassVar[OutCategory]
    OUT_CATEGORY_BYPRODUCT: _ClassVar[OutCategory]
    OUT_CATEGORY_PACKAGING: _ClassVar[OutCategory]
    OUT_CATEGORY_WIP: _ClassVar[OutCategory]
IN_CATEGORY_UNSPECIFIED: InCategory
IN_CATEGORY_RAW_MATERIAL: InCategory
IN_CATEGORY_ANCILLARY_MATERIAL: InCategory
IN_CATEGORY_TRANSPORTATION: InCategory
IN_CATEGORY_PACKAGING: InCategory
IN_CATEGORY_ENERGY: InCategory
IN_CATEGORY_UTILITY: InCategory
IN_CATEGORY_WIP: InCategory
OUT_CATEGORY_UNSPECIFIED: OutCategory
OUT_CATEGORY_EMISSION_TO_AIR: OutCategory
OUT_CATEGORY_EMISSION_TO_WATER: OutCategory
OUT_CATEGORY_EMISSION_TO_SOIL: OutCategory
OUT_CATEGORY_WASTE: OutCategory
OUT_CATEGORY_TRANSPORTATION: OutCategory
OUT_CATEGORY_SEMI_PRODUCT: OutCategory
OUT_CATEGORY_BYPRODUCT: OutCategory
OUT_CATEGORY_PACKAGING: OutCategory
OUT_CATEGORY_WIP: OutCategory
