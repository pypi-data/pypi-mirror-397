# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from bliss.shell.formatters import tabulate
from bliss.shell.formatters.table import IncrementalTable
from bliss.common.utils import RED

"""
SPEEDGOAT triggers
"""


class SpeedgoatHdwTriggerController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._triggers: dict[str, SpeedgoatHdwTrigger] | None = None
        self._load()

    def __info__(self, debug=False):
        if self._triggers is None:
            return "\n    No trigger in the model"

        if debug:
            tab = IncrementalTable(
                [["Name", "Path", "Trigger Number"]],
                col_sep=" | ",
                flag="",
                lmargin="  ",
                align="<",
            )
        else:
            tab = IncrementalTable(
                [["Name"]], col_sep=" | ", flag="", lmargin="  ", align="<"
            )

        for _trigger in self._triggers.values():
            if debug:
                tab.add_line(
                    [_trigger._name, _trigger._unique_name, _trigger.trig_number]
                )
            else:
                tab.add_line([_trigger._name])
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    def _load(self):
        triggers = self._speedgoat._get_all_objects_from_key("bliss_trigger")
        if len(triggers) > 0:
            self._triggers = {}
            for trigger in triggers:
                sp_trigger = SpeedgoatHdwTrigger(self._speedgoat, trigger)

                if hasattr(self, sp_trigger._name):
                    print(
                        f"{RED('WARNING')}: Trigger '{sp_trigger._name}' already exists"
                    )
                    return
                else:
                    setattr(self, sp_trigger._name, sp_trigger)
                    self._triggers[sp_trigger._name] = sp_trigger


class SpeedgoatHdwTrigger:
    def __init__(self, speedgoat, unique_name):
        self._speedgoat = speedgoat
        self._unique_name = unique_name

    def __info__(self):
        lines = []
        lines.append(["Name", self._name])
        lines.append(["Unique Name", self._unique_name])
        lines.append(["", ""])
        lines.append(["Number of trigs", self.trig_number])
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
            f"{self._unique_name}/bliss_trigger/String"
        )

    @property
    def trig_number(self):
        return int(self._speedgoat.signal.get(f"{self._unique_name}/trig_number"))

    def reset_trig_number(self):
        self._speedgoat.parameter.set(f"{self._unique_name}/start_trigger/Bias", 0)
        reset_trigger = int(
            self._speedgoat.parameter.get(f"{self._unique_name}/reset_trig_number/Bias")
        )
        self._speedgoat.parameter.set(
            f"{self._unique_name}/reset_trig_number/Bias", reset_trigger + 1
        )

    def trig(self):
        bias = int(
            self._speedgoat.parameter.get(f"{self._unique_name}/start_trigger/Bias")
        )
        self._speedgoat.parameter.set(
            f"{self._unique_name}/start_trigger/Bias", bias + 1
        )
