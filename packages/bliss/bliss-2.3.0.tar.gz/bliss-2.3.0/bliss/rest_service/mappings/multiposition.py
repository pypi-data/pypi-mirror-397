import logging

from bliss.rest_service.mappingdef import (
    ObjectMapping,
    HardwareProperty,
)
from ..types.multiposition import (
    MultipositionType,
    MultipositionStates,
)

logger = logging.getLogger(__name__)


class PositionsProperty(HardwareProperty):
    def translate_from(self, value):
        def normalized_target(content):
            result = {
                "object": content["axis"].name,
                "destination": content["destination"],
            }
            if "tolerance" in content:
                result["tolerance"] = content["tolerance"]
            return result

        def normalized_destination(content):
            result = {
                "position": content["label"],
                "target": [normalized_target(t) for t in content["target"]],
            }
            if "description" in content:
                result["description"] = content["description"]
            return result

        positions = [normalized_destination(p) for p in value]
        return positions


class StateProperty(HardwareProperty):
    def translate_from(self, value):
        for s in MultipositionStates:
            if value == s:
                return s


class Multiposition(ObjectMapping):
    TYPE = MultipositionType

    PROPERTY_MAP = {
        "position": HardwareProperty("position"),
        "positions": PositionsProperty("positions_list"),
        "state": StateProperty("state"),
    }

    CALLABLE_MAP = {"stop": "stop"}

    def _call_move(self, value):
        logger.debug(f"_call_move multiposition {value}")
        self._object.move(value, wait=False)


Default = Multiposition
