# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
SPEEDGOAT MOTORS
"""

import enum
from bliss.shell.formatters import tabulate
from bliss.shell.formatters.table import IncrementalTable
from bliss.common.utils import RED


class MotorState(enum.IntEnum):
    Ready = 0
    Moving = 1
    LimitNeg = 2
    LimitPos = 3
    Stopped = 4
    Error = 5


class SpeedgoatHdwMotorController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._motors: dict[str, SpeedgoatHdwMotor] | None = None
        self._load()

    def __info__(self, debug=False):
        if self._motors is None:
            return "\n    No Motor in the model"

        if debug:
            lines = [
                ["Name", "Path", "State", "Position", "Limits", "Velocity", "Acc. Time"]
            ]
        else:
            lines = [["Name", "State", "Position"]]
        tab = IncrementalTable(lines, col_sep=" | ", flag="", lmargin="  ", align="<")
        for motor in self._motors.values():
            if debug:
                tab.add_line(
                    [
                        motor._name,
                        motor._unique_name,
                        motor.state.name,
                        motor.position,
                        (motor.limit_pos, motor.limit_neg),
                        motor.velocity,
                        motor.acc_time,
                    ]
                )
            else:
                tab.add_line([motor._name, motor.state.name, motor.position])
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    def _load(self):
        motors = self._speedgoat._get_all_objects_from_key("bliss_motor")
        if len(motors) > 0:
            self._motors = {}
            for motor in motors:
                sp_motor = SpeedgoatHdwMotor(self._speedgoat, motor)

                if hasattr(self, sp_motor._name):
                    print(f"{RED('WARNING')}: Motor '{sp_motor._name}' already exists")
                    return
                else:
                    setattr(self, sp_motor._name, sp_motor)
                    self._motors[sp_motor._name] = sp_motor


class SpeedgoatHdwMotor:
    def __init__(self, speedgoat, unique_name):
        self._speedgoat = speedgoat
        self._unique_name = unique_name

    def __info__(self):
        lines = []
        lines.append(["Name", self._name])
        lines.append(["Unique Name", self._unique_name])
        lines.append(["", ""])
        lines.append(["State", self.state.name])
        lines.append(["Position", self.position])
        lines.append(["", ""])
        lines.append(["Velocity", self.velocity])
        lines.append(["Acc. Time", self.acc_time])
        lines.append(["Limit Neg.", self.limit_neg])
        lines.append(["Limit Pos.", self.limit_pos])
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
        return self._speedgoat.parameter.get(f"{self._unique_name}/bliss_motor/String")

    def start(self):
        val = self._speedgoat.parameter.get(f"{self._unique_name}/start_trigger/Bias")
        self._speedgoat.parameter.set(
            f"{self._unique_name}/start_trigger/Bias", val + 1
        )

    def stop(self):
        val = self._speedgoat.parameter.get(f"{self._unique_name}/stop_trigger/Bias")
        self._speedgoat.parameter.set(f"{self._unique_name}/stop_trigger/Bias", val + 1)

    @property
    def acc_time(self):
        return float(self._speedgoat.parameter.get(f"{self._unique_name}/acc_time"))

    @acc_time.setter
    def acc_time(self, acc_time):
        self._speedgoat.parameter.set(f"{self._unique_name}/acc_time", acc_time)

    @property
    def limit_neg(self):
        return float(self._speedgoat.parameter.get(f"{self._unique_name}/limit_neg"))

    @limit_neg.setter
    def limit_neg(self, limit_neg):
        self._speedgoat.parameter.set(f"{self._unique_name}/limit_neg", limit_neg)

    @property
    def limit_pos(self):
        return float(self._speedgoat.parameter.get(f"{self._unique_name}/limit_pos"))

    @limit_pos.setter
    def limit_pos(self, limit_pos):
        self._speedgoat.parameter.set(f"{self._unique_name}/limit_pos", limit_pos)

    @property
    def setpoint(self):
        return float(self._speedgoat.signal.get(f"{self._unique_name}/motor_setpoint"))

    @setpoint.setter
    def setpoint(self, setpoint):
        if (
            self._speedgoat.parameter.get(
                f"{self._unique_name}/select_setpoint/tracking_mode/Value"
            )
            != 0
        ):
            raise RuntimeError("Motor is in tracking mode")

        self._speedgoat.parameter.set(f"{self._unique_name}/setpoint", setpoint)

    @property
    def velocity(self):
        return float(self._speedgoat.parameter.get(f"{self._unique_name}/velocity"))

    @velocity.setter
    def velocity(self, velocity):
        self._speedgoat.parameter.set(f"{self._unique_name}/velocity", velocity)

    @property
    def position(self):
        return float(self._speedgoat.signal.get(f"{self._unique_name}/motor_position"))

    @property
    def state(self):
        return MotorState(
            int(self._speedgoat.signal.get(f"{self._unique_name}/motor_state"))
        )

    @property
    def position_encoder(self):
        if self._speedgoat.signal._tree.contains(f"{self._unique_name}/encoder_value"):
            return float(
                self._speedgoat.signal.get(f"{self._unique_name}/encoder_value")
            )

    @property
    def position_error(self):
        if self._speedgoat.signal._tree.contains(f"{self._unique_name}/error_value"):
            return float(self._speedgoat.signal.get(f"{self._unique_name}/error_value"))

    def _activate_tracking(self, tracking_enable):
        self._speedgoat.parameter.set(
            f"{self._unique_name}/select_setpoint/tracking_mode/Value", tracking_enable
        )
