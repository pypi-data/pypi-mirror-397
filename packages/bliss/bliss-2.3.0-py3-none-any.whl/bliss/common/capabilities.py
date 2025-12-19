import typing


class Capability:
    """
    Interface for any capabilities.
    """


_C = typing.TypeVar("_C", bound=Capability)


def get_capability(obj: typing.Any, capability: type[_C]) -> _C | None:
    """
    Return the implementation of the required `capability` from this `obj`.

    If the object does not provide such capability, `None` is returned.
    """
    if not hasattr(obj, "_get_capability"):
        return None
    return obj._get_capability(capability)


def get_mandatory_capability(obj: typing.Any, capability: type[_C]) -> _C:
    """
    Return the implementation of the required `capability` from this `obj`.

    Raises:
        ValueError: If this `obj` does not provide this `capability`.
    """
    if not hasattr(obj, "_get_capability"):
        obj_name = obj.name if hasattr(obj, "name") else repr(obj)
        raise ValueError(f"Object {obj_name} does not provide capabilities")
    cap = obj._get_capability(capability)
    if cap is None:
        obj_name = obj.name if hasattr(obj, "name") else repr(obj)
        raise ValueError(
            f"Object {obj_name} does not provide the capability {capability.__name__}"
        )
    return cap


class MenuCapability(Capability):
    """Allow an object `obj` to specufy the behaviour of `menu(obj)`"""

    def show_menu(self, obj: typing.Any, dialog_type: str | None = None):
        ...

    def get_menu_types(self) -> list[str]:
        """Return the available list of dialog_type"""
        return []
