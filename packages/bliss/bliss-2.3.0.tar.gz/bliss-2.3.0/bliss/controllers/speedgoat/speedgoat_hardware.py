# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Speedgoat Real Time Controller
"""

from bliss.controllers.speedgoat.speedgoat_parameter import (
    SpeedgoatHdwParameterController,
)
from bliss.controllers.speedgoat.speedgoat_signal import SpeedgoatHdwSignalController
from bliss.controllers.speedgoat.speedgoat_motor import SpeedgoatHdwMotorController
from bliss.controllers.speedgoat.speedgoat_regul import SpeedgoatHdwRegulController
from bliss.controllers.speedgoat.speedgoat_generator import (
    SpeedgoatHdwGeneratorController,
)
from bliss.controllers.speedgoat.speedgoat_filter import SpeedgoatHdwFilterController
from bliss.controllers.speedgoat.speedgoat_trigger import SpeedgoatHdwTriggerController
from bliss.controllers.speedgoat.speedgoat_ethercat import (
    SpeedgoatHdwEthercatController,
)
from bliss.controllers.speedgoat.speedgoat_lut import SpeedgoatHdwLutController
from bliss.controllers.speedgoat.speedgoat_counter import SpeedgoatHdwCounterController
from bliss.controllers.speedgoat.speedgoat_acquisition import SpeedgoatHdwAcquisition
from bliss.controllers.speedgoat.speedgoat_utils import SpeedgoatUtils

from bliss.common.utils import RED

from resyst.client.system import System
from bliss.shell.formatters import tabulate


class SpeedgoatLinuxHdwController:
    def __init__(self, name, config):
        # Set the Speedgoat Name
        self._name = name
        self._config = config

        # Connect to dance server
        self._server = config.get("server", None)
        self._port = config.get("port", None)

        self._system = System.create(f"{self._server}:{self._port}")
        self._program = self._system.running_program

        self._check_resyst_version(min_major=0, min_minor=18)

        if self._program is not None:
            self._load_objects()

    def __info__(self):
        if not self._is_app_running:
            return "No app is running"

        lines = []
        lines.append(["Speedgoat Name", self._name])
        lines.append(["Program Name", self._app_name])
        lines.append(["", ""])
        lines.append(["Cycle Time", f"{1e6 * self._Ts:.0f} us"])
        lines.append(
            [
                "Max TET",
                f"{1e6 * self._tet_max:.1f} us ({100 * self._tet_max / self._Ts:.1f}%)",
            ]
        )
        lines.append(
            ["Overloads", f"{self._overloads} (Max allowed: {self._max_overloads})"]
        )
        lines.append(["Execution Time", self._exec_time_string()])
        lines.append(["", ""])
        lines.append(["Resyst Client", self._system.version])
        lines.append(["Resyst Server", self._system.server_version])
        lines.append(["Simulink Library", f"{self._simulink_library_version:.1f}"])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="left")

    def _check_resyst_version(self, min_major=None, min_minor=None):
        clt_major, clt_minor = self._parse_resyst_version(self._system.version)
        srv_major, srv_minor = self._parse_resyst_version(self._system.server_version)

        # Check that major and minor are the same
        if (clt_major, clt_minor) != (srv_major, srv_minor):
            raise ValueError(
                f"Resyst version mismatch: client ({self._system.version}) vs server ({self._system.server_version})"
            )

        # Check minimum version if specified
        if min_major is not None and min_minor is not None:
            if (clt_major, clt_minor) < (min_major, min_minor):
                raise ValueError(
                    f"Resyst version ({self._system.version}) is lower than minimum required ({min_major}.{min_minor}.x)"
                )

    def _parse_resyst_version(self, version_str):
        """Return (major, minor) as integers from a version string 'major.minor.revision'."""
        major, minor, *_ = version_str.split(".")
        return int(major), int(minor)

    def _display_informations(self, debug=False):
        sections = []

        sections.append("Parameters")
        sections.append(self.parameter.__info__(debug=debug))

        sections.append("\n\n" + "Counters")
        sections.append(self.counter.__info__(debug=debug))

        sections.append("\n\n" + "Filters")
        sections.append(self.filter.__info__(debug=debug))

        sections.append("\n\n" + "Generators")
        sections.append(self.generator.__info__(debug=debug))

        sections.append("\n\n" + "Reguls")
        sections.append(self.regul.__info__(debug=debug))

        sections.append("\n\n" + "Motors")
        sections.append(self.motor.__info__(debug=debug))

        sections.append("\n\n" + "Triggers")
        sections.append(self.trigger.__info__(debug=debug))

        sections.append("\n\n" + "EtherCAT")
        sections.append(self.ethercat.__info__(debug=debug))

        sections.append("\n\n" + "LUT")
        sections.append(self.lut.__info__(debug=debug))

        sections.append("\n\n" + "Acquisitions")
        sections.append(self.acq.__info__(debug=debug))

        print("\n".join(sections))

    # Populate the goat_ctl object
    def _load_objects(self):
        self.parameter = SpeedgoatHdwParameterController(self)
        self.signal = SpeedgoatHdwSignalController(self)

        # Find the block were some informations are stored
        speedgoat_info_path = self._get_all_objects_from_key("bliss_speedgoat_info")
        if len(speedgoat_info_path) == 0:
            print(
                f"{RED('WARNING')}: The Simulink model does not have the 'Speedgoat Info' block"
            )
            return
        self._speedgoat_info = speedgoat_info_path[0]
        self._Ts = self._cycle_time
        self._Fs = 1 / self._Ts

        self.counter = SpeedgoatHdwCounterController(self)
        self.filter = SpeedgoatHdwFilterController(self)
        self.generator = SpeedgoatHdwGeneratorController(self)
        self.regul = SpeedgoatHdwRegulController(self)
        self.motor = SpeedgoatHdwMotorController(self)
        self.trigger = SpeedgoatHdwTriggerController(self)
        self.ethercat = SpeedgoatHdwEthercatController(self)
        self.lut = SpeedgoatHdwLutController(self)
        self.acq = SpeedgoatHdwAcquisition(self)
        self.utils = SpeedgoatUtils(self)

    # Load model on Speedgoat and run
    def _run_model(self, prg_name, force_load=False, force_run=False):
        # First check if the program is available in the Speedgoat and or the PC Server
        if prg_name not in self._program_stored_list:
            if prg_name not in self._program_loaded_list:
                raise RuntimeError(
                    f"Program file {prg_name} not found on PC server nor one the Speedgoat"
                )
            else:
                print(
                    "Program is only present in the Speedgoat and not in the PC server."
                )

        if prg_name not in self._program_loaded_list and force_load is False:
            raise RuntimeError(
                f"Program file {prg_name} not loaded in the speedgoat, use force_load=True"
            )

        # Cases to load the program
        if prg_name not in self._program_loaded_list or force_load is True:
            self._system.program_load(prg_name, overwrite=True)

        # Now run the program
        running_program = self._system.running_program
        # If program is already running and force is False: do nothing
        if (
            running_program is None
            or running_program.name != prg_name
            or force_run is True
        ):
            default_timeout = self._system.timeout
            self._system.timeout = 30
            if running_program is not None:
                self._system.program_stop()
            self._system.program_run(prg_name)
            self._program = self._system.running_program
            self._system.timeout = default_timeout
            self._load_objects()

    @property
    def _program_stored_list(self):
        return [program.name for program in self._system.stored_programs]

    @property
    def _program_loaded_list(self):
        return [program.name for program in self._system.loaded_programs]

    @property
    def _app_name(self):
        return self._program.name

    @property
    def _is_app_running(self):
        return self._system.running_program is not None

    @property
    def _tet(self):
        return self.signal.get(f"{self._speedgoat_info}/tet")

    @property
    def _tet_max(self):
        return self.signal.get(f"{self._speedgoat_info}/max_tet")

    @property
    def _cycle_time(self):
        return self.signal.get(f"{self._speedgoat_info}/Ts")

    @property
    def _exec_time(self):
        return self._cycle_time * self.signal.get(
            f"{self._speedgoat_info}/exc_time"
        )  # in [s]

    @property
    def _disk_space(self):
        return 1e-9 * self.signal.get(
            f"{self._speedgoat_info}/Get disk space"
        )  # in [Gb]

    @property
    def _memory_space(self):
        return 1e-9 * self.signal.get(
            f"{self._speedgoat_info}/Get memory info"
        )  # in [Gb]

    def _exec_time_string(self):
        seconds = int(self._exec_time)  # Ensure it's an integer
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}" + (
                f" {secs} second{'s' if secs != 1 else ''}" if secs else ""
            )
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} hour{'s' if hours != 1 else ''}" + (
                f" {minutes} minute{'s' if minutes != 1 else ''}" if minutes else ""
            )
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days} day{'s' if days != 1 else ''}" + (
                f" {hours} hour{'s' if hours != 1 else ''}" if hours else ""
            )

    def _autostart_enable(self):
        self._system.autostart_program = self._program.name

    def _autostart_disable(self):
        self._system.autostart_program = None

    def _autostart_status(self):
        if self._system.autostart_program is None:
            print("No autostart")
        else:
            print(f"Autostart program is {self._system.autostart_program.name}")

    def _reset_max_tet(self):
        self.parameter.set(
            f"{self._speedgoat_info}/reset_max_tet/Bias",
            self.parameter.get(f"{self._speedgoat_info}/reset_max_tet/Bias") + 1,
        )

    @property
    def _is_overloaded(self):
        return self._overloads >= self._max_overloads

    @property
    def _overloads(self):
        return self.signal.get(
            f"{self._speedgoat_info}/Overload Options/Overload Options Core/o1"
        )

    @property
    def _max_overloads(self):
        return self.parameter.get(f"{self._speedgoat_info}/max_overload/Value")

    @property
    def _simulink_library_version(self):
        try:
            version = self.parameter.get(
                f"{self._speedgoat_info}/bliss_speedgoat_version/Value"
            )
        except Exception:
            version = 1.0  # By default if not specified in the model
        return version

    def _get_all_objects_from_key(self, name):
        """Return identifiers of all parents whose child tag == name."""
        return [
            "/".join(param.split("/")[1:-2])
            for param in self.parameter._param_tree
            if name in param
        ]
