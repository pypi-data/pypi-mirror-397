# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
"""

import numpy
import gevent

# import time

from bliss import global_map, current_session
from bliss.common.tango import DevState, DeviceProxy
from bliss.common.logtools import log_debug
from bliss.common.axis import AxisState
from bliss.controllers.motor import Controller
from bliss.config.static import get_config
from bliss.shell.formatters import tabulate

UNDULATOR_MOTOR_TYPE = ["gap", "taper", "phase", "negoffset", "posoffset"]


class InsertionDeviceManager:
    """ """

    def __init__(self, config):

        self._name = config.get("name")
        self._config = config

        # Get a proxy on Insertion Device device server of the beamline.
        self._tango_ds_name = config.get("ds_name")
        self._tango_ds = DeviceProxy(self._tango_ds_name)
        global_map.register(
            self, parents_list=["InsertionDevice"], children_list=[self._tango_ds]
        )
        self._store_ds_name = (
            self._tango_ds_name[0 : self._tango_ds_name.index("master")] + "id/global"
        )
        self._store_ds = DeviceProxy(self._store_ds_name)

        # Get motor Aliases
        aliases = config.get("aliases", None)
        self._aliases = {}
        if aliases is not None:
            for alias in aliases:
                for name, item in alias.items():
                    self._aliases[name] = item

        # Get informations from tango server
        self._meca = {"a": None, "b": None, "c": None}
        undulator_index = 0
        for undulator_name in self._tango_ds.UndulatorNames:

            # Get the mechanic for this undulator
            position = undulator_name[-1].lower()
            is_revolver = self._tango_ds.UndulatorRevolverCarriage[undulator_index]
            if self._meca[position] is None:
                self._meca[position] = InsertionDeviceMechanic(
                    self, position, is_revolver
                )
            meca = self._meca[position]

            motor_config = {
                "plugin": "emotion",
                "package": "id24.InsertionDevice",
                "class": "InsertionDeviceTangoMotorController",
                "axes": [],
            }

            # Get Undulator
            undulator = InsertionDeviceUndulator(meca, undulator_name, undulator_index)

            # Add undulator to mechanic
            meca._add_undulator(undulator)
            meca._has_icepap_mode = undulator._has_icepap_mode

            undulator_index += 1

        # Create motors
        for meca_name, meca in self._meca.items():
            if meca is not None:
                meca._get_tango_motors(motor_config)
                if meca._has_icepap_mode:
                    meca._get_icepap_motors()
                for undulator_name, undulator in meca._undulators.items():
                    if undulator._in_beam:
                        meca._in_beam_undulator = undulator
                    setattr(self, undulator_name, undulator)

    """
    INFORMATION
    """

    def __info__(self):
        tab_str = []

        tab_str.append(
            [
                ("class:header", "Tango DS"),
                ("", f"{self._tango_ds_name}"),
                ("", " "),
            ]
        )
        tab_str.append(
            [
                ("class:header", "Status"),
                self._state_str(),
                ("", " "),
            ]
        )
        tab_str.append(
            [
                ("class:header", "Power"),
                (
                    "",
                    f"{self._tango_ds.Power:.3g} kW (max: {self._tango_ds.MaxPower:.3g} kW)",
                ),
                ("", " "),
            ]
        )
        tab_str.append(
            [
                ("class:header", "PowerDensity"),
                (
                    "",
                    f"{self._tango_ds.PowerDensity:.3g} kW/mr2 (max: {self._tango_ds.MaxPowerDensity:.3g} kW/mr2)",
                ),
                ("", " "),
            ]
        )
        fstr = tabulate.tabulate(tab_str)
        fstr += [("", "\n\n")]
        tab_str = []
        for meca_name, meca in self._meca.items():
            if meca is not None:
                tab_str.append(meca._get_info())
                info = {}
                for undulator_name, undulator in meca._undulators.items():
                    info[undulator_name] = undulator._get_info()
                    info_keys = info[undulator_name].keys()
                for key in info_keys:
                    line = [("class:header", key)]
                    for undulator_name, undulator_info in info.items():
                        line.append(undulator_info[key])
                    tab_str.append(line)
                tab_str.append(
                    [
                        ("", " "),
                        ("", " "),
                        ("", " "),
                    ]
                )
        fstr += tabulate.tabulate(tab_str)
        return fstr

    def _state(self):
        if self._tango_ds.read_attribute("State").value == DevState.DISABLE:
            return "DISABLE"
        return "ENABLE"

    def _state_str(self):
        if self._state() == "DISABLE":
            return ("class:danger", "DISABLE")
        else:
            return ("class:success", "ENABLE")

    def _motor_state(self):
        for meca_name, meca in self._meca.items():
            if meca is not None:
                print(f"MECA {meca_name}")
                for undulator_name, undulator in meca._undulators.items():
                    print(f"    UNDULATOR {undulator_name}")
                    for mot_name, mot in undulator._tango_motors.items():
                        print(f"        {mot.name} : {mot.state}")
                    if len(undulator._icepap_motors) >= 1:
                        for mot_name, mot in undulator._icepap_motors.items():
                            print(f"        {mot.name} : {mot.state}")


class InsertionDeviceMechanic:
    """ """

    def __init__(self, parent, position, is_revolver):
        self._parent = parent
        self._position = position
        self._is_revolver = is_revolver

        self._tango_ds = self._parent._tango_ds
        if is_revolver:
            self._name = f"revolver_{position}"
        else:
            self._name = f"meca_{position}"

        self._undulators = {}
        self._motors = {}

        if self._is_revolver:
            self._undulator_title = [
                ("class:header", "Undulators"),
                ("class:header", "In the beam"),
            ]
        else:
            self._undulator_title = [
                ("class:header", "Undulator"),
                ("class:header", "In the beam"),
            ]

    def __info__(self):
        tab_str = [self._get_info()]
        for undulator_name, undulator in self._undulators.items():
            tab_str.extend(undulator._get_info())
        return tabulate.tabulate(tab_str)

    def _get_info(self):
        if self._is_revolver:
            type_str = ("class:warning", "Revolver")
        else:
            type_str = ("class:warning", "Single")
        tab_str = [
            ("class:header", f"Mechanic {self._position.upper()}"),
            type_str,
            " ",
        ]
        return tab_str

    def _add_undulator(self, undulator):
        self._undulators[undulator._name] = undulator
        setattr(self, undulator._name, undulator)

    def _get_tango_motors(self, config):
        hwc = {}
        for undulator_name, undulator in self._undulators.items():
            for name, mot_hwc in undulator._motors_hwc.items():
                axis_name = f"t{mot_hwc._name}"
                if axis_name in self._parent._aliases.keys():
                    axis_name = self._parent._aliases[axis_name]
                attr_property = mot_hwc.position_limits
                axis_config = {
                    "name": axis_name,
                    "steps_per_unit": 1,
                    "low_limit": attr_property[0],
                    "high_limit": attr_property[1],
                    "unit": "mm",
                    "tolerance": 0.1,
                }
                config["axes"].append(axis_config)
                hwc[axis_name] = mot_hwc
                self._motors[mot_hwc._motor_type] = []
        self._tango_motor_controller = InsertionDeviceTangoMotorController(
            config, self._tango_ds, hwc
        )
        self._tango_motor_controller._initialize_config()
        for undulator_name, undulator in self._undulators.items():
            for name, mot_hwc in undulator._motors_hwc.items():
                axis_name = f"t{mot_hwc._name}"
                if axis_name in self._parent._aliases.keys():
                    axis_name = self._parent._aliases[axis_name]
                tango_motor = self._tango_motor_controller.get_axis(axis_name)
                if self._is_revolver:
                    setattr(tango_motor, "move_in_beam", undulator._move_in_beam)
                undulator._tango_motors[mot_hwc._motor_type] = tango_motor
                undulator._tango_motors_name[mot_hwc._motor_type] = tango_motor.name
                self._motors[mot_hwc._motor_type].append(tango_motor)
                if axis_name not in current_session.env_dict.keys():
                    current_session.env_dict[axis_name] = tango_motor

    def _get_icepap_motors(self):
        config = self._parent._config
        icepap_mode_config = config.get(f"meca_{self._position}", None)
        if icepap_mode_config is None:
            print(f"Mechanic {self._name}: No configuration for icepap mode")
            self._disable_icepap_mode()
            return
        icepap_mode_config = icepap_mode_config[0]
        self._pepu = icepap_mode_config.get("pepu", None)
        if self._pepu is None:
            print(f"Mechanic {self._name}: No pepu defined")
            self._disable_icepap_mode()
            return
        self._enc1_channel = icepap_mode_config.get("enc1_channel", None)
        if self._enc1_channel is None:
            print(f"Mechanic {self._name}: No enc1_channel defined")
            self._disable_icepap_mode()
            return
        self._enc1_scaling = icepap_mode_config.get("enc1_scaling", None)
        if self._enc1_scaling is None:
            print(f"Mechanic {self._name}: No enc1_scaling defined")
            self._disable_icepap_mode()
            return
        self._enc2_channel = icepap_mode_config.get("enc2_channel", None)
        if self._enc2_channel is None:
            print(f"Mechanic {self._name}: No enc2_channel defined")
            self._disable_icepap_mode()
            return
        self._enc2_scaling = icepap_mode_config.get("enc2_scaling", None)
        if self._enc2_scaling is None:
            print(f"Mechanic {self._name}: No enc2_scaling defined")
            self._disable_icepap_mode()
            return
        self._gap_channel = icepap_mode_config.get("gap_channel", None)
        if self._gap_channel is None:
            print(f"Mechanic {self._name}: No gap_channel defined")
            self._disable_icepap_mode()
            return
        self._taper_channel = icepap_mode_config.get("taper_channel", None)
        if self._taper_channel is None:
            if len(self._motors["taper"]) != 0:
                print(f"Mechanic {self._name}: No taper_channel defined")
                self._disable_icepap_mode()
                return
        self._force_icepap_mode = icepap_mode_config.get("force_icepap_mode", False)

        # get icepap motors
        for undulator_name, undulator in self._undulators.items():
            for undulator_motor_type in UNDULATOR_MOTOR_TYPE:
                if undulator._has_motor[undulator_motor_type]:
                    motor_name = f"m{undulator_name.lower().replace('-', '_')}{undulator_motor_type[0:3].lower()}"
                    if motor_name in self._parent._aliases.keys():
                        motor_name = self._parent._aliases[motor_name]
                    undulator._icepap_motors_name[undulator_motor_type] = motor_name
                    try:
                        mot = get_config().get(motor_name)
                        if self._is_revolver:
                            setattr(mot, "move_in_beam", undulator._move_in_beam)
                        mot._hwc = undulator._motors_hwc[undulator_motor_type]
                        attr_property = mot._hwc.position_limits
                        mot.limits = (attr_property[0], attr_property[1])
                        undulator._icepap_motors[undulator_motor_type] = mot
                        if motor_name not in current_session.env_dict.keys():
                            current_session.env_dict[
                                motor_name
                            ] = undulator._icepap_motors[undulator_motor_type]
                    except Exception:
                        undulator._icepap_motors[undulator_motor_type] = None

        # Once we get the icepap motors, we can configure undulator icepapmode
        for undulator_name, undulator in self._undulators.items():
            undulator._configure_icepap_mode()

        if self._has_icepap_mode:
            self._undulator_title.append(("class:header", "Icepap mode"))
        else:
            self._undulator_title.append(("", " "))

    def _disable_icepap_mode(self):
        self._has_icepap_mode = False
        for undulator_name, undulator in self._undulators.items():
            undulator._has_icepap_mode = False


class InsertionDeviceUndulator:
    def __init__(self, meca, undulator_name, undulator_index):

        self._name = undulator_name
        self._undulator_index = undulator_index
        self._meca = meca

        self._tango_ds = self._meca._tango_ds
        self._meca._is_revolver = self._tango_ds.UndulatorRevolverCarriage[
            undulator_index
        ]

        self._icepap_motors = {}
        self._icepap_motors_name = {}
        self._tango_motors = {}
        self._tango_motors_name = {}

        # Get tango attributes list linked with this undulator
        undulator_attr_list = []
        for attr_name in self._tango_ds.get_attribute_list():
            if attr_name.startswith(undulator_name):
                undulator_attr_list.append(attr_name)

        # Get tango attribute list per gap and taper motors
        self._has_motor = {}
        self._motors_hwc = {}
        for undulator_motor_type in UNDULATOR_MOTOR_TYPE:
            # Get tango attribute list related to undulator_motor_type motor
            attr_list = None
            for undu_attr in undulator_attr_list:
                if undu_attr.find(undulator_motor_type.upper()) != -1:
                    if attr_list is None:
                        attr_list = [undu_attr]
                    else:
                        attr_list.append(undu_attr)

            # if undulator_motor_type motor exists, get information
            if attr_list is not None:
                self._has_motor[undulator_motor_type] = True
                motor_name = f"{undulator_name.lower().replace('-', '_')}{undulator_motor_type[0:3].lower()}"
                self._motors_hwc[undulator_motor_type] = InsertionDeviceTangoMotorHwc(
                    self, motor_name, undulator_motor_type, attr_list
                )
                self._has_synchro_mode = self._motors_hwc[
                    undulator_motor_type
                ]._has_synchro_mode
                self._has_icepap_mode = self._motors_hwc[
                    undulator_motor_type
                ]._has_icepap_mode

            else:
                self._has_motor[undulator_motor_type] = False

        if self._meca._is_revolver:
            setattr(self, "move_in_beam", self._move_in_beam)

    def _configure_icepap_mode(self):
        setattr(self, "icepap_mode_on", self._icepap_mode_on)
        setattr(self, "icepap_mode_off", self._icepap_mode_off)

    def __info__(self):
        tab_str = []
        info = self._get_info()
        for key in info.keys():
            tab_str.append([("class:header", key), info[key]])
        return tabulate.tabulate(tab_str)

    def _get_info(self):
        info = {}
        # name
        info["Undulator"] = ("class:info", self._name)
        # in beam
        if self._in_beam:
            info["In the beam"] = ("class:success", "True")
        else:
            info["In the beam"] = ("class:danger", "False")
        # icepap_mode
        if self._meca._has_icepap_mode:
            icepap_mode = self._icepap_mode
            if icepap_mode is None or not icepap_mode:
                info["Icepap Mode"] = ("class:danger", "False")
            else:
                info["Icepap Mode"] = ("class:success", "True")
        for motor_type in UNDULATOR_MOTOR_TYPE:
            if motor_type in self._tango_motors.keys():
                info[f"{motor_type.upper()} Tango Motor"] = (
                    "",
                    self._tango_motors_name[motor_type],
                )
                if self._meca._has_icepap_mode:
                    info[f"{motor_type.upper()} Icepap Motor"] = (
                        "",
                        self._icepap_motors_name[motor_type],
                    )

        return info

    @property
    def _state(self):
        ustate_list = self._tango_ds.UndulatorStates
        return ustate_list[self._undulator_index]

    @property
    def _in_beam(self):
        if self._state == DevState.DISABLE:
            return False
        return True

    @property
    def _icepap_mode(self):
        # icepap mode is not available because:
        #    - not available through tango device
        #    - yml parameters are not present/correct
        if not self._has_icepap_mode:
            return None
        # Icepap mode is disable by machine
        if self._meca._parent._state() == "DISABLE":
            return False
        if not self._in_beam:
            return False
        icepap_mode = True
        for name, mot in self._motors_hwc.items():
            if not mot.icepap_mode:
                icepap_mode = False
        return icepap_mode

    def _store_move(self, axis, min_position):
        if axis.state != AxisState.DISABLED and axis._hwc.icepap_mode:
            axis._hwc.position = min_position

    def _tango_move_in_beam(self):
        self._tango_ds.Enable(self._name)
        ustate = DevState.DISABLE
        # wait for state to be neither disable nor moving
        while ustate in (DevState.DISABLE, DevState.MOVING):
            print(f"{self._name} is moving in the beam ...", end="\r")
            ustate = self._tango_ds.UndulatorStates[self._undulator_index]
            gevent.sleep(1)
        print(f"{self._name} is moving in the beam ... DONE")

    def _move_in_beam(self):
        if self._meca._parent._state() == "DISABLE":
            raise RuntimeError("Undulators are disbaled by control room")
            return
        if self._in_beam:
            return
        if self._has_icepap_mode:
            self._meca._in_beam_undulator._icepap_mode_off()
        self._tango_move_in_beam()
        self._meca._in_beam_undulator = self

    def _icepap_mode_on(self):
        if self._meca._parent._state() == "DISABLE":
            raise RuntimeError("Undulators are disbaled by control room")

        if not self._in_beam:
            raise RuntimeError(
                f"{self._name} is not in the beam. Cannot set icepap mode On"
            )

        k = 23.0 / 12.0

        # Calculate encoder values
        gap_position = self._motors_hwc["gap"].position
        if self._has_motor["taper"]:
            taper_position = self._motors_hwc["taper"].position
        else:
            taper_position = 0.0
        enc1_value = (
            gap_position - taper_position / (2.0 * k)
        ) * self._meca._enc1_scaling
        enc2_value = (
            gap_position + taper_position / (2.0 * k)
        ) * self._meca._enc2_scaling

        # Set Undulator Icepap Mode OFF
        self._motors_hwc["gap"].icepap_mode = False
        if self._has_motor["taper"]:
            self._motors_hwc["taper"].icepap_mode = False

        # Set icepap off
        self._icepap_motors["gap"].off()
        if self._has_motor["taper"]:
            self._icepap_motors["taper"].off()

        # Disable pepu outputs (gap/taper)
        self._meca._pepu.raw_write(f"CHSTATE {self._meca._gap_channel} DISABLE")
        if self._has_motor["taper"]:
            self._meca._pepu.raw_write(f"CHSTATE {self._meca._taper_channel} DISABLE")

        # write ecoders values on pepu
        self._meca._pepu.raw_write(f"CHVAL {self._meca._enc1_channel} {enc1_value}")
        self._meca._pepu.raw_write(f"CHVAL {self._meca._enc2_channel} {enc2_value}")

        # Enable pepu outputs (gap/taper)
        self._meca._pepu.raw_write(f"CHSTATE {self._meca._gap_channel} ENABLE")
        if self._has_motor["taper"]:
            self._meca._pepu.raw_write(f"CHSTATE {self._meca._taper_channel} ENABLE")

        # Set gap position on Icepap
        self._icepap_motors["gap"].dial = gap_position
        self._icepap_motors["gap"].offset = 0.0

        # Set taper position on Icepap
        if self._has_motor["taper"]:
            self._icepap_motors["taper"].dial = taper_position
            self._icepap_motors["taper"].offset = 0.0

        # Set Icepap On
        self._icepap_motors["gap"].on()
        if self._has_motor["taper"]:
            self._icepap_motors["taper"].on()

        # Set Undulator Icepap Mode ON
        self._motors_hwc["gap"].icepap_mode = True
        if self._has_motor["taper"]:
            self._motors_hwc["taper"].icepap_mode = True

        # let time for the PLC to change its control
        gevent.sleep(1)

    def _icepap_mode_off(self):

        # Set icepap off
        self._icepap_motors["gap"].off()
        if self._has_motor["taper"]:
            self._icepap_motors["taper"].off()

        # Set Undulator Icepap Mode OFF
        self._motors_hwc["gap"].icepap_mode = False
        if self._has_motor["taper"]:
            self._motors_hwc["taper"].icepap_mode = False

        gevent.sleep(1)


class InsertionDeviceTangoMotorHwc:
    def __init__(self, undulator, tango_motor_name, undulator_motor_type, attr_list):

        self._name = tango_motor_name
        self._undulator = undulator
        self._motor_type = undulator_motor_type

        self._tango_ds = self._undulator._tango_ds

        self._has_synchro_mode = False
        self._has_icepap_mode = False
        self._attr_dict = {}
        for attr_name in attr_list:
            if attr_name.find("_Position") != -1:
                self._attr_dict["Position"] = attr_name
            if attr_name.find("_Velocity") != -1:
                self._attr_dict["Velocity"] = attr_name
            if attr_name.find("_Acceleration") != -1:
                self._attr_dict["Acceleration"] = attr_name
            if attr_name.find("_SynchroMode") != -1:
                self._has_synchro_mode = True
                self._attr_dict["SynchroMode"] = attr_name
            if attr_name.find("_IcePapMode") != -1:
                self._attr_dict["IcePapMode"] = attr_name
                if self.icepap_mode is not None:
                    self._has_icepap_mode = True

    @property
    def position(self):
        if "Position" in self._attr_dict.keys():
            return self._tango_ds.read_attribute(self._attr_dict["Position"]).value

    @position.setter
    def position(self, value):
        if "Position" in self._attr_dict.keys():
            self._tango_ds.write_attribute(self._attr_dict["Position"], value)

    @property
    def velocity(self):
        if "Velocity" in self._attr_dict.keys():
            return self._tango_ds.read_attribute(self._attr_dict["Velocity"]).value

    @velocity.setter
    def velocity(self, value):
        if "Velocity" in self._attr_dict.keys():
            self._tango_ds.write_attribute(self._attr_dict["Velocity"], value)

    @property
    def acceleration(self):
        if "Acceleration" in self._attr_dict.keys():
            return self._tango_ds.read_attribute(self._attr_dict["Acceleration"]).value

    @acceleration.setter
    def acceleration(self, value):
        if "Acceleration" in self._attr_dict.keys():
            self._tango_ds.write_attribute(self._attr_dict["Acceleration"], value)

    @property
    def icepap_mode(self):
        if "IcePapMode" in self._attr_dict.keys():
            return self._tango_ds.read_attribute(self._attr_dict["IcePapMode"]).value

    @icepap_mode.setter
    def icepap_mode(self, value):
        if "IcePapMode" in self._attr_dict.keys():
            self._tango_ds.write_attribute(self._attr_dict["IcePapMode"], value)

    @property
    def synchro_mode(self):
        if "SynchroMode" in self._attr_dict.keys():
            return self._tango_ds.read_attribute(self._attr_dict["SynchroMode"]).value

    @synchro_mode.setter
    def synchro_mode(self, value):
        if "SynchroMode" in self._attr_dict.keys():
            self._tango_ds.write_attribute(self._attr_dict["SynchroMode"], value)

    @property
    def position_limits(self):
        return self._get_min_max(self._attr_dict["Position"])

    @property
    def velocity_limits(self):
        return self._get_min_max(self._attr_dict["Velocity"])

    @property
    def acceleration_limits(self):
        return self._get_min_max(self._attr_dict["Acceleration"])

    def _get_min_max(self, attr):
        attr_property = self._tango_ds.attribute_query(attr)
        if attr_property.min_value == "Not specified":
            lim_min = -numpy.inf
        else:
            lim_min = float(attr_property.min_value)
        if attr_property.max_value == "Not specified":
            lim_max = numpy.inf
        else:
            lim_max = float(attr_property.max_value)
        return (lim_min, lim_max)


class InsertionDeviceTangoMotorController(Controller):
    def __init__(self, config, tango_ds, motor_hwc):
        Controller.__init__(self, config)
        self._hwc = motor_hwc
        self._tango_ds = tango_ds

    def initialize(self):
        self.axis_settings.config_setting["acceleration"] = False
        self.axis_settings.config_setting["velocity"] = False

    def initialize_axis(self, axis):
        pass

    def finalize(self):
        pass

    def _get_subitem_default_class_name(self, cfg, parent_key):
        if parent_key == "axes":
            return "NoSettingsAxis"
        else:
            return super()._get_subitem_default_class_name(cfg, parent_key)

    def start_one(self, motion):
        if self._hwc[motion.axis.name]._undulator._meca._parent._state() == "DISABLE":
            raise RuntimeError("Undulators disabled by control room")
        if self._hwc[motion.axis.name]._undulator._in_beam:
            self._hwc[motion.axis.name].position = float(motion.target_pos)
        else:
            raise RuntimeError(
                f"Undulators {self._hwc[motion.axis.name]._undulator.name} not in the beam"
            )
        log_debug(self, f"end of start {motion.axis.name}")

    # POSITION
    def read_position(self, axis):
        if self._hwc[axis.name]._undulator._in_beam:
            return self._hwc[axis.name].position
        else:
            return numpy.nan

    def set_position(self, axis, new_position):
        """Implemented to avoid NotImplemented error in apply_config()."""
        return axis.position

    # VELOCITY
    def read_velocity(self, axis):
        if self._hwc[axis.name]._undulator._in_beam:
            return self._hwc[axis.name].velocity
        else:
            return numpy.nan

    def set_velocity(self, axis, new_velocity):
        if self._hwc[axis.name]._undulator._in_beam:
            self._hwc[axis.name].velocity = new_velocity
        else:
            raise RuntimeError(
                f"Undulators {self._hwc[axis.name]._undulator.name} not in the beam"
            )

    # ACCELERATION
    def read_acceleration(self, axis):
        if self._hwc[axis.name]._undulator._in_beam:
            return self._hwc[axis.name].acceleration
        else:
            return numpy.nan

    def set_acceleration(self, axis, new_acceleration):
        if self._hwc[axis.name]._undulator._in_beam:
            self._hwc[axis.name].acceleration = new_acceleration
        else:
            raise RuntimeError(
                f"Undulators {self._hwc[axis.name]._undulator.name} not in the beam"
            )

    # STATE
    def state(self, axis):
        # axis hardware controller
        hwc = self._hwc[axis.name]

        # Disable by control room
        if hwc._undulator._meca._parent._state() == "DISABLE":
            return AxisState("DISABLE")

        _state = hwc._undulator._state

        # Disable by revolver not in the beam
        if _state == DevState.DISABLE:
            log_debug(self, f"{axis.name} DISABLED")
            return AxisState("DISABLE")

        # moving by tango motor
        if _state == DevState.MOVING:
            log_debug(self, f"{axis.name} MOVING")
            return AxisState("MOVING")

        # Enable
        if _state == DevState.ON:
            if hwc._undulator._has_icepap_mode:
                if hwc._undulator._icepap_mode:
                    log_debug(self, f"{axis.name} DISABLED")
                    return AxisState("DISABLE")
                else:
                    log_debug(self, f"{axis.name} READY")
                    return AxisState("READY")

        log_debug(self, f"{axis.name} READY after unknown state")
        return AxisState("READY")

    def stop(self, axis):
        self._tango_ds.abort()

    def stop_all(self, *motion_list):
        self._tango_ds.abort()
