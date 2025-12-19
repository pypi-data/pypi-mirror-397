# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import enum
from functools import partial

from bliss.config.beacon_object import BeaconObject, EnumProperty
from prompt_toolkit.formatted_text import FormattedText, to_formatted_text


class ClosedLoopState(enum.Enum):
    UNDEFINED = enum.auto()
    UNKNOWN = enum.auto()
    ON = enum.auto()
    OFF = enum.auto()
    MANUAL = enum.auto()


def fget_gen(key):
    """Function used to generate specific parameters access methods"""

    def f(key, self):
        return self.axis.controller.get_closed_loop_param(self.axis, key)

    fget = partial(f, key)
    fget.__name__ = key
    return fget


def fset_gen(key):
    """Function used to generate specific parameters access methods"""

    def f(key, self, value):
        if self._setters_on:
            return self.axis.controller.set_closed_loop_param(self.axis, key, value)

    fset = partial(f, key)
    fset.__name__ = key
    return fset


class ClosedLoop(BeaconObject):
    """
    config example:
    - name: m1
      steps_per_unit: 1000
      velocity: 50
      acceleration: 1
      encoder: $m1enc
      closed_loop:
          state: on
          kp: 1
          ki: 2
          kd: 3
          settling_window: 0.1
          settling_time: 3
    """

    def __new__(cls, axis):  # pylint: disable=unused-argument
        """Make a class copy per instance to allow closed-loop objects to own
        different properties"""
        cls = type(cls.__name__, (cls,), {})
        return object.__new__(cls)

    def __init__(self, axis):
        self._axis = axis
        name = f"{axis.name}:closed_loop"
        config = axis.config.config_dict
        if isinstance(config, dict):
            super().__init__(config.get("closed_loop"), name=name)
        else:
            super().__init__(config, name=name, path=["closed_loop"])

        # Create `_state` attribute for `state` property which is the only one mandatory.
        setattr(
            self.__class__,
            "_state",
            EnumProperty("state", ClosedLoopState, must_be_in_config=True),
        )

        self._state_manual = None
        self._setters_on = False
        self._init_properties()

    def _init_properties(self):
        """Instantiate properties depending on the controller requirements"""
        reqs = self.axis.controller.get_closed_loop_requirements()
        for key in reqs:
            if hasattr(self, key):
                raise Exception(
                    f"Cannot create closed-loop property '{key}', name already exists"
                )
            setattr(
                self.__class__,
                key,
                BeaconObject.property(
                    fget=fget_gen(key), fset=fset_gen(key), must_be_in_config=True
                ),
            )

    def __info__(self):
        info_str = to_formatted_text("CLOSED-LOOP:\n")
        info_str += to_formatted_text("     state: ")

        if self.state == ClosedLoopState.ON:
            info_str += FormattedText([("class:success", "ON" + "\n")])
        if self.state == ClosedLoopState.OFF:
            info_str += FormattedText([("class:danger", "OFF" + "\n")])

        for key in self.axis.controller.get_closed_loop_requirements():
            info_str += to_formatted_text(f"     {key}: {getattr(self, key)}\n")

        try:
            info_str += to_formatted_text(
                self.axis.controller.get_closed_loop_specific_info(self.axis)
            )
        except NotImplementedError:
            pass
        except Exception as err:
            raise RuntimeError("Error getting closed-loop specific info") from err

        info_str += to_formatted_text("\n")

        return info_str

    @property
    def axis(self):
        return self._axis

    @property
    def state(self):
        """closed-loop state can be: UNDEFINED UNKNOWN ON OFF MANUAL"""
        return self._state

    def _activate(self, onoff):
        try:
            self.axis.controller.activate_closed_loop(self.axis, onoff)
        except Exception as err:
            self._state = self.axis.controller.get_closed_loop_state(self.axis)
            raise RuntimeError(
                f"Failed to turn {self.name} {'ON' if onoff else 'OFF'}"
            ) from err
        else:
            self._state = ClosedLoopState.ON if onoff else ClosedLoopState.OFF

    def on(self):
        self._activate(True)

    def off(self):
        self._activate(False)

    def _activate_setters(self):
        self._setters_on = True

    def sync_hard(self):
        """
        Force re-reading:
        * the state of the closed-loop
        * specific parameters
        from the motor controller.
        """
        self._state = self.axis.controller.get_closed_loop_state(self.axis)

        # Save setters state (to restore it later).
        setters_state = self._setters_on
        # Switch them off to be able to set specific parameters.
        self._setters_on = False

        # Read all specific parameters from hardware.
        for key in self.axis.controller.get_closed_loop_requirements():
            setattr(
                self, key, self.axis.controller.get_closed_loop_param(self.axis, key)
            )

        # Restore
        self._setters_on = setters_state

    def reset(self):
        """
        Reset error depending on the controller.
        """
        self.axis.controller.closed_loop_reset_error(self.axis)
