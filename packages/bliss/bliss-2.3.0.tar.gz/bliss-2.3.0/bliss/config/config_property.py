# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import typing
from bliss.common.utils import Undefined, UndefinedType

if typing.TYPE_CHECKING:
    from .beacon_object import BeaconObject
    from .plugins.generic import ConfigItemContainer


T = typing.TypeVar("T")


class ConfigProperty(typing.Generic[T], property):
    """
    Expose a config key as a property, that you dont want to expose
    as setting.

    The object in which the property have to expose a `.config` and `.name`
    property which is the case for `BeaconObject` and `ConfigItemContainer`.

    This provide a meaningful description, which ensure
    features like `apply_config(reload=True)` is work properly.

    In the future such description could be used by the REST API.

    This can be used the followig way:

    .. code-block::

        class Foo(BeaconObject):
            # Mandatory key from the config
            _my_prop = ConfigProperty("name_of_the_key", type=float)

            # Mandatory key which is read only
            _my_rw_prop = ConfigProperty("name_of_the_key", type=float, readonly=True)

            # Optional key.
            _my_optional_prop = ConfigProperty("name_of_the_key", type=float, default=1.0)

            # Static type checking
            _my_prop = ConfigProperty[float]("name_of_the_key")

    Arguments:
        key_in_config: Name of the key containing the value in the config.
        vtype: Ensure the type of the property. For now only basic types are supported,
               like `str`, `int`,  `bool`, but not generic like `list[str]`.
               If value is not valid, a `TypeError` is raised at initialization.
               The validation is also applied at the setting time.
        doc: Documentation for this property
        readonly: If `True` (defauult is `False`) the config key can't be set.
        default: If defined, this value will be used if the key was not found in the config.
                 If undefined, the config key have to be defined, and a `KeyError` is raised
                 at initialization if it's not the case.
                 This value is actually not tested against `vtype`.
    """

    def __init__(
        self,
        key_in_config: str,
        vtype: typing.Any = None,
        default: T | UndefinedType = Undefined,
        readonly=False,
        doc: str | None = None,
    ):
        self._key_in_config = key_in_config
        self._type = vtype
        self._default = default

        if vtype is float:
            # Assume an int is a float
            vtype = (int, float)

        def fget(self: BeaconObject | ConfigItemContainer) -> T:
            if default is Undefined:
                value = self.config[key_in_config]
            else:
                value = self.config.get(key_in_config, Undefined)
            if value is Undefined:
                value = default
            elif vtype is not None:
                if not isinstance(value, vtype):
                    raise TypeError(
                        f"Property '{key_in_config}' of the object '{self.name}' expects a {vtype}, found {type(value)}'"
                    )
            return value

        fget.__name__ = key_in_config

        def check_validity(self: BeaconObject | ConfigItemContainer):
            if vtype is not None or default is Undefined:
                fget(self)

        self._check_validity = check_validity

        if readonly:
            fset = None
        else:

            def fset(self: BeaconObject | ConfigItemContainer, value: T):
                if vtype is not None:
                    if not isinstance(value, vtype):
                        raise TypeError(
                            f"Property '{key_in_config}' of the object '{self.name}' expects a {vtype}, found {type(value)}'"
                        )
                self.config[key_in_config] = value

            fset.__name__ = key_in_config

        property.__init__(
            self,
            fget=fget,
            fset=fset,
            doc=doc,
        )
