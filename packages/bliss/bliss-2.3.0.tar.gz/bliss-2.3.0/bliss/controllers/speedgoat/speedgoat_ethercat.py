# -*- coding: utf-8 -*-
#
# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import enum
import gevent
import time

from bliss.common.user_status_info import status_message
from bliss.shell.formatters import tabulate
from bliss.shell.formatters.table import IncrementalTable
from bliss.common.utils import RED

"""
SPEEDGOAT EtherCAT
"""


class EthercatState(enum.IntEnum):
    INIT = 1
    PREOP = 2
    SAFEOP = 4
    OP = 8


class SpeedgoatHdwEthercatController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._ethercats: dict[str, SpeedgoatHdwEthercat] | None = None
        self._load()

    def __info__(self, debug=False):
        if self._ethercats is None:
            return "\n    No EtherCAT network in the model"

        if debug:
            tab = IncrementalTable(
                [["Name", "Path", "State"]],
                col_sep=" | ",
                flag="",
                lmargin="  ",
                align="<",
            )
        else:
            tab = IncrementalTable(
                [["Name", "State"]], col_sep=" | ", flag="", lmargin="  ", align="<"
            )

        for _ethercat in self._ethercats.values():
            if debug:
                tab.add_line(
                    [
                        _ethercat._name,
                        _ethercat._unique_name,
                        EthercatState(_ethercat.state).name,
                    ]
                )
            else:
                tab.add_line([_ethercat._name, EthercatState(_ethercat.state).name])
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    def _load(self):
        ethercats = self._speedgoat._get_all_objects_from_key("bliss_ethercat")
        if len(ethercats) > 0:
            self._ethercats = {}
            for ethercat in ethercats:
                sp_ethercat = SpeedgoatHdwEthercat(self._speedgoat, ethercat)

                if hasattr(self, sp_ethercat._name):
                    print(
                        f"{RED('WARNING')}: ethercat '{sp_ethercat._name}' already exists"
                    )
                    return
                else:
                    setattr(self, sp_ethercat._name, sp_ethercat)
                    self._ethercats[sp_ethercat._name] = sp_ethercat


class SpeedgoatHdwEthercat:
    def __init__(self, speedgoat, unique_name):
        self._speedgoat = speedgoat
        self._unique_name = unique_name

    def __info__(self):
        lines = []
        lines.append(["Name", self._name])
        lines.append(["Unique Name", self._unique_name])
        lines.append(["", ""])
        lines.append(["State", EthercatState(self.state).name])
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
            f"{self._unique_name}/bliss_ethercat/String"
        )

    @property
    def state(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/MasterState")

    def set_state(self, state, wait=False, display=False, timeout=10):
        self._speedgoat.parameter.set(f"{self._unique_name}/wanted_state/Value", state)
        self._speedgoat.parameter.set(
            f"{self._unique_name}/state_trigger/Bias",
            self._speedgoat.parameter.get(f"{self._unique_name}/state_trigger/Bias")
            + 1,
        )

        if wait is True:
            start_time = time.time()  # Here we suppose the acquisition has just started
            with status_message() as update:
                while self.state != state:
                    if display is True:
                        update(f" Current State: {EthercatState(self.state).name}")
                    gevent.sleep(0.2)
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Timeout while changing the EtherCAT State")
                if display is True:
                    update(f" Current State: {EthercatState(self.state).name}")
