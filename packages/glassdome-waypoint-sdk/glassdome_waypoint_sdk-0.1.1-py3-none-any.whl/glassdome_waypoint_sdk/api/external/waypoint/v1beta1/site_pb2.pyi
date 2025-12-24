from google.api import annotations_pb2 as _annotations_pb2
from glassdome_waypoint_sdk.api.protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Site(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class ListSitesRequest(_message.Message):
    __slots__ = ()
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    page_token: str
    page_size: int
    def __init__(self, page_token: _Optional[str] = ..., page_size: _Optional[int] = ...) -> None: ...

class ListSitesResponse(_message.Message):
    __slots__ = ()
    SITES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    sites: _containers.RepeatedCompositeFieldContainer[Site]
    next_page_token: str
    def __init__(self, sites: _Optional[_Iterable[_Union[Site, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...
