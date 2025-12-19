# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import gevent
import gevent.lock
import time
import re

from bliss import global_map
from bliss.comm.util import get_comm
from bliss.common.utils import autocomplete_property
from bliss.common.counter import SamplingCounter  # noqa: F401
from bliss.controllers.counter import SamplingCounterController
from bliss.common.logtools import log_debug, log_warning, log_error
from bliss.common.soft_axis import SoftAxis  # noqa: F401
from bliss.common.axis import AxisState
from bliss.controllers.bliss_controller import BlissController
from bliss.comm.serial import SerialTimeout

"""
CryogenicPS power supply, acessible via USB with Tango Serial

yml configuration example:

-  class: CryogenicPSController 
   module: powersupply.cryogenicps
   plugin: generic   
   name: cryogenic17t
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
       max: 17.1                    # defined unit (T or A)
       ramp_rate: 0.284           # (A/s)
       heater_output: 2.5         # (V)
       voltage_limit: 14.5        # (V)
       time_stabilization: 3      # (s)

   heater:
     - switching_time_off_on: 20
     - switching_time_on_off: 5
"""


class CryogenicPSCC(SamplingCounterController):
    def __init__(self, name, cryogenicps):
        super().__init__(name)
        self.cryogenicps = cryogenicps

    def read(self, counter):
        return getattr(self.cryogenicps, counter.tag)


class CryogenicPSController(BlissController):
    VALID_VALUES = [0, "off", "OFF", 1, "on", "ON"]

    def __init__(self, config):
        super().__init__(config)
        self._hardware = CryogenicPSDevice(config, self)
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
        self._tolerance = field_axis_list[0]["tolerance"]
        _mode = field_axis_list[0]["fixed_position_mode"]
        self._fixed_position_mode = str(_mode) not in ["0", "off", "false"]
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

        if self._fixed_position_mode:
            self._target_pos = self.power_supply_field
            log_debug(self, "New set point: %s", self._target_pos)
            status = self.ramp_status
            if status != "HOLDING":
                log_warning(self, "Expected HOLDING Ramp Status: got %s", status)

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

        info_list.append(f"         Fixed position mode: {self._fixed_position_mode}")

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
                as_positioner=True,
            )

    def _load_config(self):
        for cfg in self.config["counters"]:
            self._get_subitem(cfg["name"])

        self._field_axis = self._get_subitem(self.config["field_axis"][0]["name"])

    def _axis_check_position(self, expected):
        curr_pos = self.power_supply_field
        log_debug(self, "Check position: current=%s, expected=%s", curr_pos, expected)
        ok = abs(curr_pos - expected) <= self._tolerance
        if not ok:
            log_warning(
                self,
                "Too much CryoPS discrepancy: current=%s, expected=%s",
                curr_pos,
                expected,
            )
        return ok, curr_pos

    def _axis_position(self):
        """Return the actual field of the power supply as the current position of the associated soft axis."""
        if self._fixed_position_mode:
            return self._target_pos

        ## Need the beacon position ?
        power_supply_field = self.power_supply_field
        # print(f" power_supply_field: { power_supply_field}")
        return power_supply_field
        # return self.set_point_field

    def _axis_move(self, target_pos):
        # """Set the target field of the power supply a new value of the associated soft axis"""
        # if abs(target_pos - self._axis_position()) <= self._field_axis.tolerance:
        #     return

        auto_heater = self._auto_heater
        if auto_heater is None:
            raise ValueError(
                f"The Managing of the heater is wrong '{self._auto_heater}' is not acceptable. Please set it with _set_auto_heater."
            )

        if self._fixed_position_mode:
            ok, curr_pos = self._axis_check_position(self._target_pos)
            if not ok:
                raise RuntimeError(
                    f"Too much CryoPS discrepancy: current={curr_pos}, expected={self._target_pos}. "
                    f"Run {self.name}.sync_position() to continue"
                )
            if abs(self._target_pos - target_pos) < self._tolerance:
                log_debug(self, "Skipping move to %s", target_pos)
                return

        target_pos = round(target_pos, 5)
        # state = self.ramp_status
        # print(f"\n\nstate = {state}\n\n")
        # log_debug(self, "Ramp Status is %s", state)
        # if state != "HOLDING":
        #     # raise ValueError(
        #     #     f"axis {self._field_axis.name} not ready, ramp_status is '{state}'!"
        #     # )
        #     print(f"axis {self._field_axis.name} not ready, ramp_status is '{state}'!")
        #     return

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

        if self._fixed_position_mode:
            ok, curr_pos = self._axis_check_position(target_pos)
            if ok:
                self._target_pos = target_pos
                log_debug(self, "New set point: %s", self._target_pos)
            else:
                self._target_pos = curr_pos

    def _axis_stop(self):
        """Stop the motion of the associated soft axis"""
        if self._fixed_position_mode:
            return

        power_supply_field = self.power_supply_field
        self.set_point_field = power_supply_field
        while self.ramp_status != "HOLDING":
            gevent.sleep(2)
            print(
                f"Waiting field stabilization. Field is {self.power_supply_field} T.\r"
            )

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

        if self._fixed_position_mode:
            return AxisState("READY")

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

    def sync_position(self):
        if not self._fixed_position_mode:
            return

        while self.ramp_status != "HOLDING":
            gevent.sleep(2)
            log_debug(self, "Power supply value is %s", self.power_supply_field)

        # short time stabilization
        gevent.sleep(1)

        log_debug(self, "Set point: %s", self._target_pos)
        curr_pos = self.power_supply_field
        log_debug(self, "Current position: %s", curr_pos)

        print(
            f"Synchronising position: previous={self._target_pos}, current={curr_pos}"
        )
        self._target_pos = curr_pos

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

    @heater.setter
    def heater(self, value_tuple):
        """
        Set the heater to on or off
        value, heater_time = value_tuple
        """
        self.hardware._heater = value_tuple

    def _set_heater(self, val):
        """Set the Switch heater status"""
        if val not in list(self.VALID_VALUES):
            raise ValueError(f"Wrong value '{val}'. Should be in {self.VALID_VALUES}")
        if val == 1:
            val = "ON"
        elif val == 0:
            val = "OFF"

        heater_time = (
            self._heater_time_off_on if val == "ON" else self._heater_time_on_off
        )

        if val == "ON" and self._fixed_position_mode:
            ok, curr_pos = self._axis_check_position(self._target_pos)
            if not ok:
                raise RuntimeError(
                    f"Too much CryoPS discrepancy: current={curr_pos}, "
                    f"expected={self._target_pos}. "
                    f"Run {self.name}.sync_position() to continue"
                )

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

    ASW_PREFIX_RE = re.compile("(.{8}|[0-9]{2}(:[0-9]{2}){2})")

    def __init__(self, config, logger_instance):
        self._logger_instance = logger_instance
        self._config = config
        self._comm = None
        max_freq = self._config.get("comm_max_frequency", 20)
        self.comm_waiting_time = 1 / max_freq
        self.comm_last_call = 0
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
        return self.send_cmd("GET OUTPUT", get_filter=float)

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
        return self.send_cmd("GET TPA", get_filter=float)

    @property
    def max_position(self):
        """Max position"""
        return self.send_cmd("GET MAX", get_filter=float)

    @property
    def voltage_limit(self):
        """Output voltage limit"""
        return self.send_cmd("GET VL", get_filter=float)

    @property
    def set_point_field(self):
        """Field in T"""
        return self.send_cmd("GET MID", get_filter=float)

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

    def send_cmd(
        self, command, arg=None, heater_time=None, full_asw=False, get_filter=str
    ):
        """Send a command to the controller.

        Arguments:
            command (str): The command string
            args: Possible variable number of parameters

        Returns:
            Answer from the controller
        """

        logger = self._logger_instance

        log_debug(logger, "In send_cmd")
        # limitation of commands flow
        delta_t = time.perf_counter() - self.comm_last_call
        log_debug(logger, "Time before the last cmd is %.3f ms", delta_t * 1000)
        if delta_t <= self.comm_waiting_time:
            time.sleep(self.comm_waiting_time - delta_t)
            log_debug(
                logger,
                "Waiting time between 2 cmds is %.3f ms",
                (self.comm_waiting_time - delta_t) * 1000,
            )

        log_debug(logger, "\t command is %s", command)
        if arg is not None:
            log_debug(logger, "\t arg is %s", arg)

        if heater_time is not None:
            log_debug(logger, "\t heater_time is %s", heater_time)

        max_retries = 5
        for attempt in range(1, max_retries + 1):
            # flush comm before attempt
            self.comm.flush()

            try:
                is_setter = arg is not None
                arg_str = f" {arg}" if is_setter else ""
                cmd = (command + arg_str + "\n").encode()

                with self.comm.lock:
                    self.comm.write(cmd, timeout=self._timeout)
                    if command.startswith("RAMP") and is_setter:
                        return

                    if command.startswith("HEATER") and is_setter:
                        for i in range(heater_time):
                            if (heater_time - i) > 9:
                                print(
                                    f"Switching heater to {arg}: {heater_time - i}\t",
                                    end="\r",
                                )
                            else:
                                print(
                                    f" Switching heater to {arg}: {heater_time - i}\t",
                                    end="\r",
                                )

                            gevent.sleep(1)
                        print("                               ", end="\r")

                    reply = self.comm.readline(eol="\n", timeout=self._timeout)
                    log_debug(logger, "Write command is %s, reply is %s", cmd, reply)
                    if full_asw:
                        return reply

                asw_cmd, asw_val = self._parse_reply(reply)
                if command.startswith("TESLA"):
                    assert asw_cmd == "UNITS", f"Bad answer command: {asw_cmd}"
                elif command.startswith("GET OUTPUT"):
                    assert asw_cmd == "OUTPUT", f"Bad answer command: {asw_cmd}"
                elif command.startswith("HEATER"):
                    assert asw_cmd == "HEATER STATUS", f"Bad answer command: {asw_cmd}"
                    asw = asw_val.split()
                    if asw[0] in ["ON", "OFF"]:
                        return get_filter(asw[0])
                    elif asw[0] == "SWITCHED":
                        assert asw[1] == "OFF", f"Bad SWITCHED value: {asw[1]}"
                        return get_filter("OFF")
                    else:
                        raise ValueError(f"Bad HEATER answer value: '{asw_val}'")

                assert asw_val, f"Bad answer value: {asw_val}"
                return get_filter(asw_val.split()[0])

            except SerialTimeout as e:
                log_error(logger, f"Connection attempt #{attempt} failed: {e}")
                if attempt == max_retries:
                    raise RuntimeError("Max communication retries exceeded. Exiting.")

                self.comm.flush()
                time.sleep(1)

            except Exception as e:
                log_error(logger, f"Error in attempt #{attempt}: {e}")
                if attempt == max_retries:
                    raise RuntimeError("Max communication retries exceeded. Exiting.")

            finally:
                self.comm_last_call = time.perf_counter()

    def _parse_reply(self, reply):
        logger = self._logger_instance

        if isinstance(reply, bytes):
            reply = reply.decode()
        reply = reply.strip()

        try:
            prefix = reply[:8]
            assert self.ASW_PREFIX_RE.match(prefix) is not None, "Bad prefix"
            assert reply[8] == " ", "Missing separator"
            tokens = reply[9:].split(":")
            asw_cmd = tokens[0].strip()
            asw_val = ":".join(tokens[1:]).strip()
            return asw_cmd, asw_val
        except Exception as e:
            msg = f'Error parsing reply "{reply}": {e}'
            log_error(logger, msg)
            raise RuntimeError(msg)
