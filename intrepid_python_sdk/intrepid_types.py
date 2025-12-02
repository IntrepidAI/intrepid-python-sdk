from pydantic import BaseModel
from typing import Dict, Any, Awaitable, Callable, Generic, NewType, TypeVar, get_args, get_origin

# Special types
T = TypeVar('T')
class Context(Generic[T]):
    state: T | None
    debug_log_callback: Callable[[str], Awaitable[None]]

    def __init__(self, state: T | None, debug_log_callback: Callable[[str], Awaitable[None]]):
        self.state = state
        self.debug_log_callback = debug_log_callback

    async def debug_log(self, message: str) -> None:
        await self.debug_log_callback(message)

# Intrepid primitive types
Boolean = NewType("Boolean", bool)
F32 = NewType("F32", float)
F64 = NewType("F64", float)
I8 = NewType("I8", int)
I16 = NewType("I16", int)
I32 = NewType("I32", int)
I64 = NewType("I64", int)
I128 = NewType("I128", int)
U8 = NewType("U8", int)
U16 = NewType("U16", int)
U32 = NewType("U32", int)
U64 = NewType("U64", int)
U128 = NewType("U128", int)
String = NewType("String", str)
Text = NewType("Text", str)

class Vec2(BaseModel):
    x: float
    y: float

class Vec3(BaseModel):
    x: float
    y: float
    z: float

class Vec4(BaseModel):
    x: float
    y: float
    z: float
    w: float

class Bivec2(BaseModel):
    xy: float

class Bivec3(BaseModel):
    yz: float
    zx: float
    xy: float

class Rotor2(BaseModel):
    s: float
    xy: float

class Rotor3(BaseModel):
    s: float
    yz: float
    zx: float
    xy: float


TYPE_MAP: Dict[type, str] = {
    bool: "boolean",
    float: "f64",
    int: "i64",
    str: "string",
    Boolean: "boolean",
    F32: "f32",
    F64: "f64",
    I8: "i8",
    I16: "i16",
    I32: "i32",
    I64: "i64",
    I128: "i128",
    U8: "u8",
    U16: "u16",
    U32: "u32",
    U64: "u64",
    U128: "u128",
    String: "string",
    Text: "text",
    Vec2: "vec2",
    Vec3: "vec3",
    Vec4: "vec4",
    Bivec2: "bivec2",
    Bivec3: "bivec3",
    Rotor2: "rotor2",
    Rotor3: "rotor3",
}
