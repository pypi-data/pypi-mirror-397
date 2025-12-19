from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeedBoostResult(_message.Message):
    __slots__ = ["config_id", "execution_number", "identifier_field", "response", "timestamp"]
    CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    config_id: int
    execution_number: int
    identifier_field: str
    response: str
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, identifier_field: _Optional[str] = ..., response: _Optional[str] = ..., config_id: _Optional[int] = ..., execution_number: _Optional[int] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
