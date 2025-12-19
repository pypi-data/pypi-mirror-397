# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""

"""

from bliss.common.logtools import log_debug
from bliss.common.axis import Axis, AxisState, lazy_init
from bliss.common.tango import DevState


class UndulatorAxis(Axis):
    def __init__(self, name, controller, config):

        Axis.__init__(self, name, controller, config)

        self._hwc = None

    @property
    @lazy_init
    def state(self):
        """Return the axis state
        Return:
             AxisState: axis state"""
        if self.is_moving:
            return AxisState("MOVING")

        # really read from hw
        state = self.hw_state
        self.settings.set("state", state)
        return state

    @property
    @lazy_init
    def hw_state(self):
        """Return the current hardware axis state (:obj:`AxisState`)"""

        if self._hwc is None:
            log_debug(self, f"{self.name} DISABLED: No Hardware controller")
            return AxisState("DISABLE")

        # Disable by control room
        if self._hwc._undulator._meca._parent.state() == "DISABLE":
            log_debug(self, f"{self.name} DISABLED: Disable by control room")
            return AxisState("DISABLE")

        _state = self._hwc._undulator._state

        # Disable by revolver not in the beam
        if _state == DevState.DISABLE:
            log_debug(
                self,
                f"{self.name} DISABLED: Undulator {self._hwc._undulator._name} not in the beam",
            )
            return AxisState("DISABLE")

        # moving by tango motor
        if _state == DevState.MOVING and not self._hwc._undulator._icepap_mode:
            log_debug(self, f"{self.name} DISABLED: MOVING by tango motor")
            return AxisState("DISABLE")

        # Enable
        if _state == DevState.ON:
            if self._hwc._undulator._has_icepap_mode:
                # Disable by not in icepapmode
                if not self._hwc._undulator._icepap_mode:
                    if self._hwc._undulator._meca._force_icepap_mode:
                        self._hwc._undulator.icepap_mode_on()
                        state = self.controller.state(self)
                        log_debug(self, f"{self.name} {state.current_states_names[0]}")
                        return state
                    else:
                        log_debug(self, f"{self.name} DISABLED: Not in Icepap Mode")
                        return AxisState("DISABLE")
                # State defined by icepap state
                else:
                    state = self.controller.state(self)
                    log_debug(self, f"{self.name} {state.current_states_names[0]}")
                    return state

        log_debug(self, f"{self.name} READY after unknown state")
        return AxisState("READY")
