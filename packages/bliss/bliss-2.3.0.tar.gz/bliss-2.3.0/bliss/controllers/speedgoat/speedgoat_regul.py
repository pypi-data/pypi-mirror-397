# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
SPEEDGOAT REGULATOR
"""

import numpy as np
import enum
from bliss.common.utils import RED
from bliss.shell.formatters.table import IncrementalTable
from bliss.shell.formatters import tabulate


class RegulState(enum.IntEnum):
    Off = 0
    On = 1


class RegulError(enum.IntEnum):
    NoError = 0
    MinInput = 1
    MaxInput = 2
    MinOutput = 3
    MaxOutput = 4
    ExtError = 5


class SpeedgoatHdwRegulController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._reguls: dict[str, SpeedgoatHdwRegul] | None = None
        self._load()

    def __info__(self, debug=False):
        if self._reguls is None:
            return "\n    No Regulator in the model"

        if debug:
            tab = IncrementalTable(
                [["Name", "Path", "Wanted", "State", "Error", "Input", "Output"]],
                col_sep=" | ",
                flag="",
                lmargin="  ",
                align="<",
            )
        else:
            tab = IncrementalTable(
                [["Name", "Wanted", "State"]],
                col_sep=" | ",
                flag="",
                lmargin="  ",
                align="<",
            )

        for _regul in self._reguls.values():
            if debug:
                tab.add_line(
                    [
                        _regul._name,
                        _regul._unique_name,
                        _regul.wanted,
                        _regul.ctrl_status.name,
                        _regul.ctrl_error.name,
                        _regul.error_signal,
                        _regul.command_signal,
                    ]
                )
            else:
                tab.add_line([_regul._name, _regul.wanted, _regul.ctrl_status.name])
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    def _load(self):
        reguls = self._speedgoat._get_all_objects_from_key("bliss_regulator")
        if len(reguls) > 0:
            self._reguls = {}
            for regul in reguls:
                sp_regul = SpeedgoatHdwRegul(self._speedgoat, regul)

                if hasattr(self, sp_regul._name):
                    print(
                        f"{RED('WARNING')}: Regulator '{sp_regul._name}' already exists"
                    )
                    return
                else:
                    setattr(self, sp_regul._name, sp_regul)
                    self._reguls[sp_regul._name] = sp_regul


class SpeedgoatHdwRegul:
    def __init__(self, speedgoat, unique_name):
        self._speedgoat = speedgoat
        self._unique_name = unique_name

    def __info__(self):
        lines = []
        lines.append(["Name", self._name])
        lines.append(
            [
                "Wanted",
                ("class:success", "True")
                if self.wanted
                else ("class:warning", "False"),
            ]
        )
        if self.ctrl_status == 0:
            lines.append(["State", ("class:warning", self.ctrl_status.name)])
            lines.append(["Error", ("class:warning", self.ctrl_error.name)])
            if self.ctrl_error != 0:
                lines.append(
                    [
                        "  Output at error",
                        "["
                        + ", ".join(f"{x:.2g}" for x in np.ravel(self.command_fault))
                        + "]",
                    ]
                )
                lines.append(
                    [
                        "  Intput at error",
                        "["
                        + ", ".join(f"{x:.2g}" for x in np.ravel(self.error_fault))
                        + "]",
                    ]
                )
        else:
            lines.append(["State", ("class:success", self.ctrl_status.name)])
        lines.append(["", ""])
        lines.append(
            [
                "Current Error",
                "[" + ", ".join(f"{x:.2g}" for x in np.ravel(self.error_signal)) + "]",
            ]
        )
        lines.append(
            [
                "Current Command",
                "["
                + ", ".join(f"{x:.2g}" for x in np.ravel(self.command_signal))
                + "]",
            ]
        )
        lines.append(["", ""])
        lines.append(
            [
                "Error Limits",
                "["
                + ", ".join(
                    f"{x:.2g}" for x in [self.error_lower_limit, self.error_upper_limit]
                )
                + "]",
            ]
        )
        lines.append(
            [
                "Command Limits",
                "["
                + ", ".join(
                    f"{x:.2g}"
                    for x in [self.command_lower_limit, self.command_upper_limit]
                )
                + "]",
            ]
        )
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    def _tree(self):
        print("Parameters:")
        self._speedgoat.parameter._tree.subtree(
            self._speedgoat._program.name + "/" + self._unique_name
        ).show()
        print("Signals:")
        self._speedgoat.signal._tree.subtree(
            self._speedgoat._program.name + "/" + self._unique_name
        ).show()

    @property
    def _name(self):
        return self._speedgoat.parameter.get(
            f"{self._unique_name}/bliss_regulator/String"
        )

    @property
    def error_lower_limit(self):
        """Minimum allowed input (usually control error)"""
        return self._speedgoat.parameter.get(f"{self._unique_name}/error_lower_limit")

    @error_lower_limit.setter
    def error_lower_limit(self, value):
        if value < self.error_upper_limit:
            self._speedgoat.parameter.set(
                f"{self._unique_name}/error_lower_limit", value
            )
        else:
            raise ValueError(
                f"error_lower_limit {value} must be < {self.error_upper_limit}"
            )

    @property
    def error_upper_limit(self):
        """Maximum allowed input (usually control error)"""
        return self._speedgoat.parameter.get(f"{self._unique_name}/error_upper_limit")

    @error_upper_limit.setter
    def error_upper_limit(self, value):
        if value > self.error_lower_limit:
            self._speedgoat.parameter.set(
                f"{self._unique_name}/error_upper_limit", value
            )
        else:
            raise ValueError(
                f"error_upper_limit {value} must be > {self.error_lower_limit}"
            )

    @property
    def command_lower_limit(self):
        """Mimum allowed output (usually control command signal)"""
        return self._speedgoat.parameter.get(f"{self._unique_name}/command_lower_limit")

    @command_lower_limit.setter
    def command_lower_limit(self, value):
        if value < self.command_upper_limit:
            self._speedgoat.parameter.set(
                f"{self._unique_name}/command_lower_limit", value
            )
        else:
            raise ValueError(
                f"command_lower_limit {value} must be < {self.command_upper_limit}"
            )

    @property
    def command_upper_limit(self):
        """Maximum allowed output (usually control command signal)"""
        return self._speedgoat.parameter.get(f"{self._unique_name}/command_upper_limit")

    @command_upper_limit.setter
    def command_upper_limit(self, value):
        if value > self.command_lower_limit:
            self._speedgoat.parameter.set(
                f"{self._unique_name}/command_upper_limit", value
            )
        else:
            raise ValueError(
                f"command_upper_limit {value} must be > {self.command_lower_limit}"
            )

    @property
    def error_fault(self):
        """Stored input (usually error signal) when the regul was last turned OFF."""
        return self._speedgoat.signal.get(f"{self._unique_name}/error_fault")

    @property
    def command_fault(self):
        """Stored command signal when the regul was last turned OFF."""
        return self._speedgoat.signal.get(f"{self._unique_name}/command_fault")

    @property
    def wanted(self):
        """Is the regul is wanted?"""
        return bool(int(self._speedgoat.signal.get(f"{self._unique_name}/ctrl_wanted")))

    def on(self):
        """Turn the regul ON"""
        self.reset_error()
        self._speedgoat.parameter.set(f"{self._unique_name}/wanted/Value", 1)

    def off(self):
        """Turn the regul OFF"""
        self._speedgoat.parameter.set(f"{self._unique_name}/wanted/Value", 0)

    def reset_error(self):
        """If the regul was OFF due to too large input or output, reset the error to be
        able to turn it ON again."""
        reset_error = int(
            self._speedgoat.parameter.get(f"{self._unique_name}/reset_error/Bias")
        )
        self._speedgoat.parameter.set(
            f"{self._unique_name}/reset_error/Bias", reset_error + 1
        )

    @property
    def fault_time(self):
        """IF the regul goes from ON to OFF, time it takes to put the command signal at zero."""
        return self._speedgoat.parameter.get(f"{self._unique_name}/fault_time")

    @fault_time.setter
    def fault_time(self, value):
        if value <= 0:
            raise ValueError("fault_time must be positive")
        self._speedgoat.parameter.set(f"{self._unique_name}/fault_time", value)

    @property
    def fault_output(self):
        """IF the regul goes from ON to OFF, the output signal will be fault_output."""
        return self._speedgoat.parameter.get(f"{self._unique_name}/fault_output")

    @fault_output.setter
    def fault_output(self, value):
        self._speedgoat.parameter.set(f"{self._unique_name}/fault_output", value)

    @property
    def ctrl_error(self):
        """It regul is OFF due to some error, display this error."""
        # 0:no_error 1:min_input_reached 2:max_input_reached 3:min_output_reached 4:max_output_reached 5:ext_error
        return RegulError(
            int(self._speedgoat.signal.get(f"{self._unique_name}/ctrl_error"))
        )

    @property
    def ctrl_status(self):
        # 0:off 1:on
        return RegulState(
            int(self._speedgoat.signal.get(f"{self._unique_name}/ctrl_status"))
        )

    @property
    def error_signal(self):
        """Regul input, usually error signal."""
        return self._speedgoat.signal.get(f"{self._unique_name}/error_signal")

    @property
    def command_signal(self):
        """Regul output, usually command signal."""
        return self._speedgoat.signal.get(f"{self._unique_name}/command_signal")
