from enum import Enum
from pydantic import BaseModel, ModelWrapValidatorHandler, model_serializer, model_validator
from typing import Any, Optional, Self


class Empty(BaseModel):
    pass

class FlowSocket(BaseModel):
    label: str
    exec_id: int

class DataSocket(BaseModel):
    label: str
    type: str
    data: Optional[Any] = None

class InitCommand(BaseModel):
    node_id: str
    node_type: str
    exec_inputs: list[FlowSocket]
    exec_outputs: list[FlowSocket]
    data_inputs: list[DataSocket]
    data_outputs: list[DataSocket]

class ExecCommand(BaseModel):
    exec_id: int
    time: int
    inputs: list[Any]

class ExecReply(BaseModel):
    exec_id: int
    outputs: list[Any]

class DiscoveryOptions(BaseModel):
    init_timeout: float
    exec_timeout: float
    #allow_multiplexing: bool

class DiscoveryPinTypeKind(str, Enum):
    FLOW = "flow"
    DATA = "data"
    WILDCARD = "wildcard"
    ANY = "any"
    ANY_OR_FLOW = "any_or_flow"

class DiscoveryPinType(BaseModel):
    kind: DiscoveryPinTypeKind
    data_type: Optional[str] = None
    wildcard_index: Optional[int] = None

    @model_serializer
    def serialize_model(self) -> Any:
        if self.kind == DiscoveryPinTypeKind.DATA:
            return {"data": self.data_type if self.data_type is not None else ""}
        if self.kind == DiscoveryPinTypeKind.WILDCARD:
            return {"wildcard": self.wildcard_index if self.wildcard_index is not None else 0}
        return self.kind.value

    @model_validator(mode='wrap')
    @classmethod
    def validate_model(cls, value: Any, handler: ModelWrapValidatorHandler[Self]) -> Any:
        if isinstance(value, str):
            return cls(kind=DiscoveryPinTypeKind(value))
        if isinstance(value, dict):
            if value.get("kind"):
                return handler(value)
            if set(value.keys()) == {"data"} and isinstance(value["data"], str):
                return cls(kind=DiscoveryPinTypeKind.DATA, data_type=value["data"])
            elif set(value.keys()) == {"wildcard"} and isinstance(value["wildcard"], int):
                return cls(kind=DiscoveryPinTypeKind.WILDCARD, wildcard_index=value["wildcard"])
        if isinstance(value, DiscoveryPinType):
            return value
        raise TypeError("DiscoveryPinType must be a string or dict {data: str} or {wildcard: int}")

class DiscoveryPinContainer(str, Enum):
    SINGLE = "single"
    OPTION = "option"
    ARRAY = "array"
    ANY = "any"

class DiscoveryPinCount(str, Enum):
    ONE = "one"
    ZERO_OR_MORE = "zero_or_more"

class DiscoveryPinSpec(BaseModel):
    label: str
    description: Optional[str] = None
    type: DiscoveryPinType
    container: Optional[DiscoveryPinContainer] = None
    count: Optional[DiscoveryPinCount] = None
    default_count: Optional[int] = None
    default: Optional[Any] = None
    is_const: Optional[bool] = None

class DiscoveryNodeSpec(BaseModel):
    type: str
    label: str
    description: Optional[str] = None
    inputs: Optional[list[DiscoveryPinSpec]] = None
    outputs: Optional[list[DiscoveryPinSpec]] = None

class DiscoveryTypeSpec(BaseModel):
    type: str
    description: Optional[str] = None
    fields: list[tuple[str, str]]

class Discovery(BaseModel):
    options: DiscoveryOptions
    types: list[DiscoveryTypeSpec]
    nodes: list[DiscoveryNodeSpec]

class IncomingMessage(BaseModel):
    id: int
    node: Optional[int] = None
    discovery: Optional[Empty] = None
    init: Optional[InitCommand] = None
    exec: Optional[ExecCommand] = None

    @model_validator(mode="after")
    def validate_enum(self) -> Self:
        count = 0
        if self.discovery is not None:
            count += 1
        if self.init is not None:
            count += 1
        if self.exec is not None:
            count += 1
        if count != 1:
            raise ValueError("exactly one of `discovery`, `init`, or `exec` must be present")
        return self

class OutgoingMessage(BaseModel):
    id: int
    node: Optional[int] = None
    discovery_ok: Optional[Discovery] = None
    init_ok: Optional[Empty] = None
    exec_ok: Optional[ExecReply] = None
    error: Optional[str] = None
    debug_message: Optional[str] = None

    @model_validator(mode="after")
    def validate_enum(self) -> Self:
        count = 0
        if self.discovery_ok is not None:
            count += 1
        if self.init_ok is not None:
            count += 1
        if self.exec_ok is not None:
            count += 1
        if self.error is not None:
            count += 1
        if self.debug_message is not None:
            count += 1
        if count != 1:
            raise ValueError("exactly one of `discovery_ok`, `init_ok`, `exec_ok`, `error`, or `debug_message` must be present")
        return self
