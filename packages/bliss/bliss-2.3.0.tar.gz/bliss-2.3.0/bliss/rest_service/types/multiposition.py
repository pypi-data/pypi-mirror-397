import logging
from typing import Literal, Optional
from typing_extensions import TypedDict, NotRequired

from bliss.rest_service.typedef import (
    ObjectType,
    HardwareSchema,
    Field,
    CallableSchema,
    Callable1Arg,
    EmptyCallable,
)

logger = logging.getLogger(__name__)

MultipositionStates = ["MOVING", "READY", "UNKNOWN", "ERROR"]


class MultipositionAxis(TypedDict):
    object: str
    destination: float | str
    tolerance: NotRequired[float]


class MultipositionPosition(TypedDict):
    position: str
    description: NotRequired[str]
    target: list[MultipositionAxis]


class MultipositionPropertiesSchema(HardwareSchema):
    state: Optional[Literal[tuple(MultipositionStates)]] = Field(None, read_only=True)
    position: Optional[str] = None
    positions: list[MultipositionPosition] = Field(read_only=True)


class MultipositionCallablesSchema(CallableSchema):
    move: Callable1Arg[str]
    stop: EmptyCallable


class MultipositionType(ObjectType):
    NAME = "multiposition"
    STATE_OK = [MultipositionStates[0], MultipositionStates[1]]

    PROPERTIES = MultipositionPropertiesSchema
    CALLABLES = MultipositionCallablesSchema


Default = MultipositionType
