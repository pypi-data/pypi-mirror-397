# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
SPEEDGOAT Lookup Tables
"""

import numpy as np
from bliss.shell.formatters import tabulate
from bliss.shell.formatters.table import IncrementalTable
from bliss.common.utils import GREEN, RED


class SpeedgoatHdwLutController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._luts: dict[str, SpeedgoatHdwLut] | None = None
        self._load()

    def __info__(self, debug=False):
        if self._luts is None:
            return "\n    No LUT in the model"

        if debug:
            tab = IncrementalTable(
                [["Name", "Path", "Enabled"]],
                col_sep=" | ",
                flag="",
                lmargin="  ",
                align="<",
            )
        else:
            tab = IncrementalTable(
                [["Name", "Enabled"]], col_sep=" | ", flag="", lmargin="  ", align="<"
            )
        for _lut in self._luts.values():
            if debug:
                tab.add_line(
                    [
                        _lut._name,
                        _lut._unique_name,
                        GREEN("True") if _lut.enabled else RED("False"),
                    ]
                )
            else:
                tab.add_line(
                    [_lut._name, GREEN("True") if _lut.enabled else RED("False")]
                )
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    def _load(self, force=False):
        luts = self._speedgoat._get_all_objects_from_key("bliss_lut")
        if len(luts) > 0:
            self._luts = {}
            for _lut in luts:
                sp_lut = SpeedgoatHdwLut(self._speedgoat, _lut)

                if hasattr(self, sp_lut._name):
                    print(f"{RED('WARNING')}: LUT '{sp_lut._name}' already exists")
                    return
                else:
                    setattr(self, sp_lut._name, sp_lut)
                    self._luts[sp_lut._name] = sp_lut


class SpeedgoatHdwLut:
    def __init__(self, speedgoat, unique_name):
        self._speedgoat = speedgoat
        self._unique_name = unique_name

    def __info__(self):
        lines = []
        lines.append(["", ""])
        lines.append(["Name", self._name])
        lines.append(["Unique Name", self._unique_name])
        lines.append(
            [
                "Enabled",
                ("class:success", "True")
                if self.enabled
                else ("class:warning", "False"),
            ]
        )
        y_raw = self.y_raw
        lines.append(
            ["X raw", f"[{y_raw[0]}, {y_raw[1]}, ..., {y_raw[-2]}, {y_raw[-1]}]"]
        )
        x_raw = self.x_raw
        lines.append(
            ["Y raw", f"[{x_raw[0]}, {x_raw[1]}, ..., {x_raw[-2]}, {x_raw[-1]}]"]
        )
        lines.append(["", ""])
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
        return self._speedgoat.parameter.get(f"{self._unique_name}/bliss_lut/String")

    def enable(self):
        self._speedgoat.parameter.set(f"{self._unique_name}/enable/Value", 1)

    def disable(self):
        self._speedgoat.parameter.set(f"{self._unique_name}/enable/Value", 0)

    @property
    def length(self):
        return len(self.x_raw)

    @property
    def enabled(self):
        return bool(self._speedgoat.parameter.get(f"{self._unique_name}/enable/Value"))

    @property
    def y_raw(self):
        return np.squeeze(self._speedgoat.parameter.get(f"{self._unique_name}/y_raw"))

    @y_raw.setter
    def y_raw(self, value):
        self._speedgoat.parameter.set(f"{self._unique_name}/y_raw", value)

    @property
    def x_raw(self):
        return np.squeeze(self._speedgoat.parameter.get(f"{self._unique_name}/x_raw"))

    @x_raw.setter
    def x_raw(self, value):
        self._speedgoat.parameter.set(f"{self._unique_name}/x_raw", value)

    @property
    def y_input(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/y_input")

    @property
    def y_output(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/y_output")

    @property
    def x_data(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/x_data")

    @property
    def y_data(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/y_data")
