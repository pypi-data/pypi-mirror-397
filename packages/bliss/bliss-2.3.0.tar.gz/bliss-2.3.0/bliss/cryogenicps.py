# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import gevent
import gevent.lock

from bliss import global_map
from bliss.comm.util import get_comm
from bliss.common.utils import autocomplete_property
from bliss.common.counter import SamplingCounter  # noqa: F401
from bliss.controllers.counter import SamplingCounterController
from bliss.common.logtools import log_debug
from bliss.common.soft_axis import SoftAxis  # noqa: F401
from bliss.common.axis import AxisState
from bliss.controllers.bliss_controller import BlissController

"""
CryogenicPS power supply, acessible via USB with Tango Serial

yml configuration example:

-  class: CryogenicPSController
   module: powersupply.mryogenicps
   plugin: generic
   name: ipsox8tid12 # ulmag7tps
   serial:
     url: tango://id12/serial_124/usb0   

   counters:
     - name : set_point_cryosm_field
       tag: set_point_field
     - name :  power_supply_cryosm_field
       tag: power_supply_field
     - name : sweep_rate_cryosm_field
       tag: ramp_rate
      
   field_axis:
     - name: cryosm
       tolerance: 0.01
       steps_per_unit: 1
       unit: TESLA                # TESLA or AMP
       conversion_factor: 0.11339 # (T/A)       
       max: 17                    # defined unit (T or A)
       ramp_rate: 0.284           # (A/s)
       heater_output: 2.5         # (V)
       voltage_limit: 14.5        # (V)
       time_stabilization: 3      # (s)

   heater:
     - switching_time_off_on: 20
     - switching_time_on_off: 10
"""


class CryogenicPSCC(SamplingCounterController):
    def __init__(self, name, mryogenicps):
        super().__init__(name)
        self.mryogenicps = mryogenicps

    def read(self, counter):
        return getattr(self.mryogenicps, counter.tag)


class CryogenicPSController(BlissController):
    VALID_VALUES = [0, "off", "OFF", 1, "on", "ON"]

    def __init__(self, config):
        super().__init__(config)
        self._hardware = CryogenicPSDevice(config)
        self._scc = CryogenicPSCC(self.name, self._hardware)
        global_map.register(self, parent_list=["controllers", "counters"])
        self._auto_heater = True
        heater_list = self.config["heater"]
        self._heater_time_off_on = heater_list[0]["switching_time_off_on"]
        self._heater_time_on_off = heater_list[1]["switching_time_on_off"]
        field_axis_list = self.config["field_axis"]
        self._unit = field_axis_list[0]["unit"]
        self._conversion_factor = field_axis_list[0]["conversion_factor"]
        self._max_position = field_axis_list[0]["max"]
        self._ramp_rate = field_axis_list[0]["ramp_rate"]
        self._heater_output = field_axis_list[0]["heater_output"]
        self._voltage_limit = field_axis_list[0]["voltage_limit"]
        self._time_stabilization = field_axis_list[0]["time_stabilization"]
        self._stop = False
        self._hardware.comm.flush()
        conversion_factor = float(self._conversion_factor)
        self._hardware.send_cmd("SET TPA", conversion_factor)
        if self._unit == "TESLA":
            self._hardware.send_cmd("TESLA", arg=1)
        else:
            self._hardware.send_cmd("TESLA", arg=0)

        max_position = float(self._max_position)
        self._hardware.send_cmd("SET MAX", arg=max_position)
        ramp_rate = float(self._ramp_rate)
        self._hardware.send_cmd("SET RAMP", ramp_rate)
        heater_output = float(self._heater_output)
        self._hardware.send_cmd("SET HEATER", arg=heater_output)
        voltage_limit = float(self._voltage_limit)
        self._hardware.send_cmd("SET VL", arg=voltage_limit)

    def __info__(self, show_module_info=True):
        info_list = []
        print(f"\nGathering information from {self._config['serial'].to_dict()}:")
        info_list.append("")
        info_list_byte = self._hardware.comm.write_readlines(
            "UPDATE\n".encode(), nb_lines=16, eol="\r\n"
        )
        self._hardware.comm.raw_read()  # for the last unused char
        conversion_factor = self._hardware.send_cmd("GET TPA")
        conversion_factor_info = "........ TESLA PER AMPS: " + conversion_factor
        info_list.append(conversion_factor_info)
        for list_byte in info_list_byte:
            info_list.append(list_byte.decode())

        return "\n".join(info_list)

    def _get_subitem_default_class_name(self, cfg, parent_key):
        if parent_key == "counters":
            return "SamplingCounter"

        elif parent_key == "field_axis":
            return "SoftAxis"

    def _create_subitem_from_config(
        self, name, cfg, parent_key, item_class, item_obj=None
    ):
        if parent_key == "counters":
            mode = cfg.get("mode", "MEAN")
            unit = cfg.get("unit", "")
            obj = self._scc.create_counter(item_class, name, mode=mode, unit=unit)
            obj.tag = cfg["tag"]
            return obj
        elif parent_key == "field_axis":
            return item_class(
                name,
                self,
                position=self._axis_position,
                move=self._axis_move,
                stop=self._axis_stop,
                state=self._axis_state,
                low_limit=-cfg.get("max"),
                high_limit=cfg.get("max"),
                tolerance=cfg.get("tolerance", 0.01),
                unit="T",
                export_to_session=False,
            )

    def _load_config(self):
        for cfg in self.config["counters"]:
            self._get_subitem(cfg["name"])

        self._field_axis = self._get_subitem(self.config["field_axis"][0]["name"])

    def _axis_position(self):
        """Return the actual field of the power supply as the current position of the associated soft axis."""
        ## Need the beacon position ?
        power_supply_field = self.power_supply_field
        return power_supply_field

    def _axis_move(self, target_pos):
        """Set the target field of the power supply a new value of the associated soft axis"""
        auto_heater = self._auto_heater
        if auto_heater is None:
            raise ValueError(
                f"The Managing of the heater is wrong '{self._auto_heater}' is not acceptable. Please set it with _set_auto_heater."
            )

        target_pos = round(target_pos, 5)
        state = self.ramp_status
        log_debug(self, "Ramp Status is %s", state)
        if state != "HOLDING":
            raise ValueError(
                f"axis {self._field_axis.name} not ready, ramp_status '{state}'!"
            )

        pos_polarity = self._hardware._get_sign()
        pos_polarity = "+" if pos_polarity == "POSITIVE" else "-"
        target_pos_polarity = "+" if target_pos >= 0 else "-"
        change_direction = True if pos_polarity != target_pos_polarity else False
        time_stabilization = self._time_stabilization
        if auto_heater:
            self._set_heater("ON")

        if change_direction:
            log_debug(self, "Ramp Status is %s", self.ramp_status)
            self.set_point_field = 0
            log_debug(self, "Set field to 0")
            log_debug(self, "Ramp Status is %s", self.ramp_status)
            while self.ramp_status != "HOLDING":
                gevent.sleep(2)
                log_debug(self, "Power supply value is %s", self.power_supply_field)

            # short time stabilization at zero
            gevent.sleep(1)
            self._hardware._set_polarity(target_pos_polarity)

        log_debug(self, "Ramp Status is %s", self.ramp_status)
        self.set_point_field = target_pos
        log_debug(self, "Set target position to %s", target_pos)
        log_debug(self, "Ramp Status is %s", self.ramp_status)
        while self.ramp_status != "HOLDING":
            gevent.sleep(2)
            log_debug(self, "Power supply value is %s", self.power_supply_field)

        log_debug(self, "Waiting current stabilisation for %ss", time_stabilization)
        for i in range(time_stabilization):
            print(
                f"Waiting current stabilisation: {time_stabilization - i}\t", end="\r"
            )
            gevent.sleep(1)

        print("                                                         ", end="\r")
        if auto_heater:
            self._set_heater("OFF")

    def _axis_stop(self):
        """Stop the motion of the associated soft axis"""
        self._stop = True

    def _axis_state(self):
        """Return the current state of the associated soft axis."""
        # Standard axis states:
        # MOVING : 'Axis is moving'
        # READY  : 'Axis is ready to be moved (not moving ?)'
        # FAULT  : 'Error from controller'
        # LIMPOS : 'Hardware high limit active'
        # LIMNEG : 'Hardware low limit active'
        # HOME   : 'Home signal active'
        # OFF    : 'Axis is disabled (must be enabled to move (not ready ?))'

        if self._stop:
            self._stop = False
            return AxisState("READY")

        state = self.ramp_status
        if state == "HOLDING":
            return AxisState("READY")
        elif state == "RAMPING":
            return AxisState("MOVING")
        else:
            return AxisState("FAULT")

    @autocomplete_property
    def counters(self):
        return self._scc.counters

    @autocomplete_property
    def hardware(self):
        return self._hardware

    @property
    def power_supply_field(self):
        """Field in T of the"""
        return self.hardware.power_supply_field

    @property
    def unit(self):
        """Field in T or A"""
        return self.hardware.tesla

    @property
    def teslaperamps(self):
        """Conversionfactor"""
        return self.hardware.teslaperamps

    @property
    def max_position(self):
        """Max position"""
        return self.hardware.max_position

    @property
    def voltage_limit(self):
        """Max position"""
        return self.hardware.voltage_limit

    @property
    def time_stabilization(self):
        """Waiting time stabilization of the current output"""
        return self._time_stabilization

    @property
    def set_point_field(self):
        """Field in T (T done in the init)"""
        return self.hardware.set_point_field

    @set_point_field.setter
    def set_point_field(self, value):
        """Target field in T (T done in the init)"""
        self.hardware.set_point_field = value

    @property
    def ramp_rate(self):
        """Target ramp rate in A/s"""
        return self.hardware.ramp_rate

    @property
    def ramp_status(self):
        """Reads the alarm flags for the device (HexFormat)"""
        return self.hardware.ramp_status

    @property
    def heater(self):
        """Reads the Switch heater status"""
        return self.hardware._heater

    def _set_heater(self, val):
        """Set the Switch heater status"""
        if val not in list(self.VALID_VALUES):
            raise ValueError(f"Wrong value '{val}'. Should be in {self.VALID_VALUES}")
        if val == 1:
            val = "ON"
            heater_time = self._heater_time_off_on
        elif val == 0:
            val = "OFF"
            heater_time = self._heater_time_on_off
        # else:
        #     val = val.upper()
        if val == "ON":
            heater_time = self._heater_time_off_on
        elif val == "OFF":
            heater_time = self._heater_time_on_off

        log_debug(self, "The heater is switching to %s for %ss", val, heater_time)
        self.hardware._heater = (val, heater_time)

    def _set_auto_heater(self, val):
        """Enable or disable the managing of the heater duing a motion.
        Arguments:
            command (str): the command string
            args: enable or disable

        Returns:
            None
        """
        if val not in ["enable", "disable"]:
            raise ValueError(f"Wrong value '{val}'. Should be enable or disable")
        if val == "enable":
            self._auto_heater = True
        else:
            self._auto_heater = False


class CryogenicPSDevice:
    def __init__(self, config):
        self._config = config
        self._comm = None
        self._timeout = config.get("timeout", 2.9)
        self._lock = gevent.lock.Semaphore()

    def __str__(self):
        # this is for the mapping: it needs a representation of instance
        return super().__repr__()

    @property
    def comm(self):
        if self._comm is None:
            self._comm = get_comm(self._config)
        return self._comm

    @property
    def power_supply_field(self):
        """Field in T"""
        return float(self.send_cmd("GET OUTPUT"))

    @property
    def tesla(self):
        """Field in T or A"""
        return self.send_cmd("TESLA")

    @tesla.setter
    def tesla(self, value):
        """Field in T or A"""
        self.send_cmd("TESLA", value)

    @property
    def teslaperamps(self):
        """Read the conversionfactor"""
        return float(self.send_cmd("GET TPA"))

    @property
    def max_position(self):
        """Max position"""
        return float(self.send_cmd("GET MAX"))

    @property
    def voltage_limit(self):
        """Output voltage limit"""
        return float(self.send_cmd("GET VL"))

    @property
    def set_point_field(self):
        """Field in T"""
        return float(self.send_cmd("GET MID"))

    @set_point_field.setter
    def set_point_field(self, value):
        """Set the target value field in T"""
        self.send_cmd("SET MID", value)
        self.send_cmd("RAMP", "MID")

    @property
    def ramp_rate(self):
        """Target ramp rate in A/s"""
        return float(self.send_cmd("GET RATE"))

    @ramp_rate.setter
    def ramp_rate(self, value):
        """Set the value ramp rate in A/s"""
        self.send_cmd("SET RAMP", value)

    @property
    def ramp_status(self):
        """Reads ramp status: HOLDING, RAMPING, QUENCH or EXTERNAL"""
        return self.send_cmd("RAMP STATUS")

    @property
    def _heater(self):
        """Reads the Switch heater status"""
        heater = self.send_cmd("HEATER")
        return heater

    @_heater.setter
    def _heater(self, value_tuple):
        """Set the Switch heater status (check before set)"""
        value, heater_time = value_tuple
        heater_state = self.send_cmd("HEATER")
        if value == heater_state:
            print(f"Heater is already {heater_state}.\n")
        else:
            self.send_cmd("HEATER", value, heater_time=heater_time)

    def _get_sign(self):
        return self.send_cmd("GET SIGN")

    def _set_polarity(self, sign):
        self.send_cmd("DIRECTION", arg=sign)

    def send_cmd(self, command, arg=None, heater_time=None, full_asw=False):
        """Send a command to the controller.

        Arguments:
            command (str): The command string
            args: Possible variable number of parameters

        Returns:
            Answer from the controller
        """

        if arg is None:
            cmd = (command + "\n").encode()
            reply = self.comm.write_readline(cmd, eol="\n", timeout=1)
            reply = reply.decode()
            if full_asw:
                return reply

            asw = reply.split()
            if reply.count(":") == 1:
                if command.find("TESLA") == 0:
                    return asw[2]
                elif asw[3] == "SWITCHED":
                    return "OFF"
                else:
                    return asw[3]
            elif reply.count(":") == 3:
                return asw[2]
            else:
                raise ValueError(f"Error. Answer '{reply}' is not 'VALID'.")
        else:
            arg = str(arg)
            cmd = f"{command} {arg}\n"
            cmd = cmd.encode()
            self.comm.write(cmd, timeout=1)
            if command.find("RAMP") == 0:
                return

            if command.find("HEATER") == 0:
                for i in range(heater_time):
                    if (heater_time - i) > 9:
                        print(
                            f"Switching heater to {arg}: {heater_time - i}\t", end="\r"
                        )
                    else:
                        print(
                            f" Switching heater to {arg}: {heater_time - i}\t", end="\r"
                        )

                    gevent.sleep(1)

                print("                               ", end="\r")

            reply = (self.comm.readline(eol="\n", timeout=1)).decode()
            if reply.count(":") < 1:
                raise ValueError(
                    f"Argument '{arg}' is not 'VALID' because the answer is {asw}."
                )
