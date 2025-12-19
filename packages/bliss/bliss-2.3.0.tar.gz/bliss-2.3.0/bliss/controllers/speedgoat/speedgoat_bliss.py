# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Speedgoat BLISS support.
"""

import gevent
import numpy as np

from bliss.shell.cli.user_dialog import UserChoice
from bliss.shell.standard import show_dialog

from bliss import global_map
from bliss.common.axis import AxisState
from bliss.shell.standard import print_html
from bliss.common.logtools import log_debug
from bliss.common.utils import autocomplete_property, object_attribute_get
from bliss.common.counter import SamplingCounter, SamplingMode
from bliss.scanning.acquisition.counter import SamplingCounterAcquisitionSlave
from bliss.scanning.chain import AcquisitionMaster, AcquisitionSlave
from bliss.controllers.counter import SamplingCounterController
from bliss.controllers.bliss_controller import BlissController
from bliss.controllers.motor import Controller

from bliss.controllers.speedgoat.speedgoat_counter import SpeedgoatHdwCounter


class SpeedgoatController(BlissController):
    """Bliss controller for Speedgoat machine"""

    def __init__(self, config):
        BlissController.__init__(self, config)

        global_map.register(self, parents_list=["counters"])

        # Speedgoat Hardware controller
        self._hwc = self._config.get("speedgoat_hardware_controller")

        # Counter controller
        self._scc = SpeedgoatCountersController(self)

    def _load_config(self):
        """
        Read and apply the YML configuration of this container
        """
        pass

    def _init(self):
        """
        Place holder for any action to perform after the configuration has been loaded.
        """
        pass

    @autocomplete_property
    def counters(self):
        return self._scc.counters

    def __info__(self):
        """Command line info string"""
        txt = self.get_info()
        return txt

    def get_info(self):
        """Return controller info as a string"""
        return f"Speedgoat Controller {self.name}"

    def run_model(self):
        # Suppose this is your list
        programs = self._hwc._program_stored_list

        # Convert it to (value, label) tuples
        choices = [(p, p) for p in programs]

        dlg = UserChoice(label="List of stored programs", values=choices)
        program_name = show_dialog(dlg, title="Choose program")
        if program_name is not None:
            self._hwc._run_model(program_name, force_load=True, force_run=True)
            # Update counters
            self._scc._init_counters()

    def add_signal_counter(self, name, path, description=None, unit=None, force=False):
        # Add the counter in goat_ctl
        self._hwc.counter._add_counter(
            name, path, description=description, unit=unit, force=force
        )
        # Add it to the goat object
        SpeedgoatCounter(name, {}, self._scc)
        global_map.register(self, parents_list=["counters"])


class SpeedgoatMotorController(Controller):
    """Bliss Motor controller for Speedgoat machine"""

    def _load_config(self):
        super()._load_config()
        self.speedgoat = self.config.get("speedgoat_hardware_controller", None)

        self.speedgoat_names = {}
        self.speedgoat_motors = {}
        for name, config in self._axes_config.items():
            sp_name = config.get("speedgoat_name")
            if sp_name not in self.speedgoat.motor._motors.keys():
                raise RuntimeError(f"Motor {sp_name} not in Speedgoat Model")
            self.speedgoat_names[name] = sp_name
            self.speedgoat_motors[name] = self.speedgoat.motor._motors[sp_name]

        self._axis_init_done = {}

    def initialize_axis(self, axis):
        if (
            axis.name not in self._axis_init_done.keys()
            or self._axis_init_done[axis.name] is False
        ):
            self._axis_init_done[axis.name] = True
            spg_low = self.speedgoat_motors[axis.name].limit_neg
            spg_high = self.speedgoat_motors[axis.name].limit_pos
            cfg_low = axis.config.config_dict.get("low_limit", spg_low)
            cfg_high = axis.config.config_dict.get("high_limit", spg_high)

            try:
                axis.low_limit = max(cfg_low, spg_low)
                axis.high_limit = min(cfg_high, spg_high)

            except Exception:
                self._axis_init_done[axis.name] = False

    def read_position(self, axis):
        return self.speedgoat_motors[axis.name].position

    def read_velocity(self, axis):
        return self.speedgoat_motors[axis.name].velocity

    def set_velocity(self, axis, new_velocity):
        acc = self.read_acceleration(axis)
        self.speedgoat_motors[axis.name].velocity = new_velocity
        self.speedgoat_motors[axis.name].acc_time = new_velocity / acc

    def read_acceleration(self, axis):
        acc_time = self.speedgoat_motors[axis.name].acc_time
        velocity = self.speedgoat_motors[axis.name].velocity
        return velocity / acc_time

    def set_acceleration(self, axis, new_acc):
        acc_time = self.speedgoat_motors[axis.name].velocity / new_acc
        self.speedgoat_motors[axis.name].acc_time = acc_time

    def state(self, axis):
        # speedgoat motor states: 0: ready 1:moving 2:lim_neg 3:lim_pos 4:stopped 5:error
        if not self.speedgoat._is_app_running:
            return AxisState("OFF")
        state = self.speedgoat_motors[axis.name].state
        if state == 1:
            return AxisState("MOVING")
        if state == 2:
            return AxisState("LIMNEG")
        if state == 3:
            return AxisState("LIMPOS")
        if state == 5:
            return AxisState("FAULT")
        return AxisState("READY")

    def prepare_move(self, motion):
        self.speedgoat_motors[motion.axis.name].setpoint = motion.target_pos

    def start_one(self, motion):
        if not self._is_regul_on(motion.axis):
            raise RuntimeError(f"regulation of axis {motion.axis.name} is OFF")

        self.speedgoat_motors[motion.axis.name].start()

    def start_all(self, *motions):
        for m in motions:
            self.start_one(m)

    def stop_one(self, axis):
        self.speedgoat_motors[axis.name].stop()

    def stop_all(self, *motions):
        for m in motions:
            self.stop_one(m.axis)

    def set_limits(self, axis, limits):
        self.speedgoat_motors[axis.name].limit_neg = limits[0]
        self.speedgoat_motors[axis.name].limit_pos = limits[1]
        axis.limits = limits

    def _is_regul_on(self, axis):
        regul_name = axis.config.config_dict.get("regul_name")
        if regul_name is None:
            return True

        if self.speedgoat.regul._reguls is None:
            raise RuntimeError(
                "Cannot check regulation state because this model does not define any regulation"
            )

        regul = self.speedgoat.regul._reguls[regul_name]
        return bool(regul.state.value)

    def _activate_tracking(self, axis, tracking_enable):
        self.speedgoat_motors[axis.name]._activate_tracking(tracking_enable)

    @object_attribute_get(type_info="float")
    def get_EncoderPos(self, axis):
        return self.speedgoat_motors[axis.name].position_encoder

    @object_attribute_get(type_info="float")
    def get_PositionError(self, axis):
        return self.speedgoat_motors[axis.name].position_error


class SpeedgoatCountersController(SamplingCounterController):
    """Bliss Counter controller for Speedgoat machine"""

    def __init__(self, speedgoat):
        super().__init__(f"{speedgoat._name}_scc", register_counters=False)
        self.speedgoat = speedgoat
        self._init_counters()

    def _init_counters(self):
        if hasattr(self.speedgoat._hwc, "counter"):
            for cnt_name in self.speedgoat._hwc.counter._counters:
                SpeedgoatCounter(cnt_name, {}, self)
            global_map.register(self.speedgoat, parents_list=["counters"])

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        trigger_type = acq_params.pop("trigger_type", "SOFTWARE")
        if trigger_type == "HARDWARE":
            # Get filter signal
            filter_path = None
            if self.speedgoat._config.get("filter_counter") is not None:
                filter_path = self.speedgoat.counters[
                    self.speedgoat._config.get("filter_counter")
                ]._full_path
            if self.speedgoat._config.get("filter_path") is not None:
                filter_path = self.speedgoat._config.get("filter_path")
            if filter_path is None:
                print_html("<warning>WARNING: Filter Signal not specified</warning>")

            return SpeedgoatRingBufferAcquisitionSlave(
                self,
                ctrl_params=ctrl_params,
                filter_path=filter_path,
                **acq_params,
            )
        else:
            return SamplingCounterAcquisitionSlave(
                self, ctrl_params=ctrl_params, **acq_params
            )

    def get_default_chain_parameters(self, scan_params, acq_params):
        if "count_time" in acq_params.keys():
            count_time = acq_params["count_time"]
        else:
            count_time = scan_params["count_time"]

        if "npoints" in acq_params.keys():
            npoints = acq_params["npoints"]
        else:
            npoints = scan_params["npoints"]

        trigger_type = acq_params.get("trigger_type", "SOFTWARE")

        return {
            "count_time": count_time,
            "npoints": npoints,
            "trigger_type": trigger_type,
        }

    def read_all(self, *counters):
        values = []
        for cnt in counters:
            values.append(cnt.read())
        return values


class SpeedgoatCounter(SamplingCounter):
    """Bliss SamplingCounter for Speedgoat machine"""

    def __init__(self, name, config, controller):
        self._speedgoat = controller.speedgoat
        self._speedgoat_counter = controller.speedgoat._hwc.counter._counters[name]
        self._full_path = self._speedgoat_counter._full_path

        self._unit = self._speedgoat_counter.unit

        super().__init__(name, controller, mode=SamplingMode.LAST, unit=self._unit)

        self._shape = self._speedgoat._hwc.signal._signal_tree[self._full_path].shape

    def read(self):
        return self._speedgoat_counter.value

    @property
    def shape(self):
        return self._shape


class SpeedgoatRingBufferAcquisitionSlave(AcquisitionSlave):
    """Acquisition slave corresponding to Speedgoat Ring Buffer"""

    def __init__(
        self, acq_controller, npoints=1, ctrl_params=None, filter_path=None, **kwargs
    ):

        prepare_once = kwargs.get("prepare_once", False)
        start_once = kwargs.get("start_once", False)

        AcquisitionSlave.__init__(
            self,
            acq_controller,
            npoints=npoints,
            trigger_type=AcquisitionMaster.HARDWARE,
            prepare_once=prepare_once,
            start_once=start_once,
            ctrl_params=ctrl_params,
        )

        self.__stop_flag = False

        self._speedgoat = acq_controller.speedgoat
        self._acq = self._speedgoat._hwc.acq
        self._acq_name = "trig_ringbuffer"

        self._filter_path = filter_path

        self.nb_points = npoints

    def add_counter(self, counter):
        # Automatically select "goat.counters.counter_name" if "goat_ctl.counter.counter_name" is passed instead
        if isinstance(counter, SpeedgoatHdwCounter):
            counter = self._speedgoat.counters[counter.name]

        if hasattr(counter, "_speedgoat_counter"):
            if isinstance(counter._speedgoat_counter, SpeedgoatHdwCounter):
                super().add_counter(counter)
            else:
                print(
                    f"Warning: Counter ({counter.name}) is not valid for RingBuffer Acquisition"
                )
        else:
            print(
                f"Warning: Counter ({counter.name}) is not valid for RingBuffer Acquisition"
            )

    def wait_ready(self):
        # return only when ready
        return True

    def prepare(self):
        # Automatically remove the previous ring_buffer acquisition object
        if self._acq_name in [x.name for x in self._speedgoat._hwc._program.acqs]:
            self._speedgoat._hwc._program.remove_acq(self._acq_name)
        self._acq.prepare(
            self.nb_points,
            list(self._counters.keys()),
            name=self._acq_name[5:],
            filter_path=self._filter_path,
        )
        log_debug(
            self._speedgoat,
            "prepared nbpoints=%s for counters=%s",
            self.nb_points,
            [x.name for x in self._counters],
        )
        self.__stop_flag = False

    def start(self):
        # Start speedgoat DAQ device
        self._acq.start(wait=False, silent=True, name=self._acq_name)

    def stop(self):
        # Set the stop flag to stop the reading process
        self._acq.stop(name=self._acq_name)
        self.__stop_flag = True

    def reading(self):
        """Function used by BLISS during zap scans or time scans"""
        point_acquired_total = 0
        acq = self._acq._get_acq_from_name(name=self._acq_name)
        # Get data until Ring Buffer as register all the data
        while (acq._is_running) and (not self.__stop_flag) and (not acq.is_done):
            point_acquired = acq.nb_sample_to_read
            point_acquired_total += point_acquired
            data_acq = acq.get_data(point_acquired)

            data = {}
            for signal_path in acq.signal_paths:
                counter_name = self._speedgoat._hwc.counter._get_counter_from_full_path(
                    signal_path
                ).name
                val = data_acq[signal_path]
                if isinstance(val, np.ndarray):
                    val = val.astype("float")
                else:
                    val = float(val)
                data[counter_name] = val
            self.channels.update(data)

            self.emit_progress_signal({"nb_points": point_acquired_total})

            gevent.sleep(10e-3)

        if acq.nb_sample_to_read > 0:
            point_acquired = acq.nb_sample_to_read
            point_acquired_total += point_acquired
            data_acq = acq.get_data(point_acquired)

            data = {}
            for signal_path in acq.signal_paths:
                counter_name = self._speedgoat._hwc.counter._get_counter_from_full_path(
                    signal_path
                ).name
                val = data_acq[signal_path]
                if isinstance(val, np.ndarray):
                    val = val.astype("float")
                else:
                    val = float(val)
                data[counter_name] = val
            self.channels.update(data)

            self.emit_progress_signal({"nb_points": point_acquired_total})
