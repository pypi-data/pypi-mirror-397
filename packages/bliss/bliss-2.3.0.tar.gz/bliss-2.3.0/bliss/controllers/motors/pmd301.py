# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import gevent
import gevent.lock

from bliss import global_map
from bliss.comm.util import get_comm, TCP
from bliss.common import greenlet_utils
from bliss.common.axis.state import AxisState
from bliss.common.utils import object_method
from bliss.common.logtools import log_debug, log_error
from bliss.controllers.motor import Controller


# TODO: lazy init...


class PMD301(Controller):
    """Bliss controller for PiezoMotor PMD301 piezo motor controller (RS422)"""

    ctrl_axis = None
    ctrl_status = ""
    axis_status = {}

    def __init__(self, *args, **kwargs):
        Controller.__init__(self, *args, **kwargs)
        self.lock = gevent.lock.RLock()

    def initialize(self):
        """
        Called in session startup.
        Open a single communication socket to the controller all chained axes.
        """
        # set acceleration config not mandatory
        self.axis_settings.config_setting["acceleration"] = False

        try:
            self.sock = get_comm(self.config.config_dict, TCP)
        except Exception:
            self.ctrl_status = "PMD301 Initialized"
            raise RuntimeError(self.ctrl_status)

        # TODO : add timeout 1s
        self.axes_count = self.config.get("axes_count")
        self._isHalfDuplex = self.config.get("half_duplex", False)

        global_map.register(self, children_list=[self.sock])

        log_debug(self, "socket open : %r", self.sock)

        self.ctrl_status = "PMD301 Initialized"

    def finalize(self):
        """
        Close the controller socket.
        """
        self.sock.close()
        log_debug(self, "socket closed: %r", self.sock)

    def initialize_axis(self, axis):
        """
        Called at first axis usage.
        """
        chan = axis.config.get("chan_number", int)
        if (chan >= 0) and (chan < 127) and isinstance(chan, int):
            axis.chan_number = chan
        else:
            print(f"error in {self.name} config : chan_number must be in [0..126]")

        # Store first axis number to talk to the controller.
        if self.ctrl_axis is None:
            self.ctrl_axis = axis

    def get_axis_info(self, axis):
        """
        Info for axis.
        """
        info_str = f"PMD301 axis {axis.name}\n"
        info_str += f"    channel number:{axis.chan_number}\n"
        info_str += "    status=" + self.get_motor_status(axis) + "\n"

        info_str += self.get_info(axis)

        return info_str

    def __info__(self):
        """
        inline info for PMD301 controller.
        """
        info_str = "PMD301 controller\n"
        info_str += f"  number of chained device(s): {self.axes_count}\n"
        info_str += f"  com:{self.sock}\n"

        return info_str

    def _wait_for_state(self, axis, state, equal=True, timeout=10, sleeptime=0.02):
        """Wait for the given state.
        - equal=True:  return when state in curr_state
        - equal=False: return when state not in curr_state
        """
        with greenlet_utils.timeout(timeout):
            while True:
                curr_state = self.state(axis)
                if (state in curr_state) == equal:
                    return
                gevent.sleep(sleeptime)

    def initialize_encoder(self, encoder):
        pass

    def set_on(self, axis):
        """
        Unpark axis + power ON + reset CL.
        """
        self.unpark_motor(axis)
        self._wait_for_state(axis, "OFF", equal=False)
        self.closed_loop_reset_error(axis)

    def set_off(self, axis):
        """
        Park axis + power OFF
        """
        self.park_motor(axis)
        self._wait_for_state(axis, "OFF")

    def home_search(self, axis, switch):
        """
        Search the home around the current position
        """

        self.send(axis, "J10,0,10")
        self._wait_for_state(axis, "MOVING", equal=False)

        self.send(axis, "N4")
        self.send(axis, "J-20,0,10")
        self._wait_for_state(axis, "MOVING", equal=False)

    def home_state(self, axis):
        return self.state(axis)

    def read_position(self, axis):
        """
        Return position's setpoint (in controller units).

        Args:
            - <axis> : bliss axis.
        Return:
            - <position> : float :
        """
        ans = self.send(axis, "T")
        setpoint = float(ans)
        return setpoint

    def read_encoder(self, encoder):
        """
        Return measured position (in encoder units)
        """
        ans = self.send(encoder.axis, "E")
        meas_pos = float(ans)
        return meas_pos

    # Velocity  NOT (YET) MANAGED ????
    # For now, fixed for safety reasons.
    def read_velocity(self, axis):
        """
        Fake method...
        """
        return 1

    def set_velocity(self, axis, new_velocity):
        """
        Fake method...
        """
        log_debug(self, "%s velocity NOT written : %d ", axis.name, new_velocity)
        return 1

    # Acceleration NOT (YET) MANAGED ????
    #
    #    def read_acctime(self, axis):
    #        """
    #        Return acceleration time in seconds.
    #        """
    #        return 1
    #
    #    def set_acctime(self, axis, new_acctime):
    #        return 1

    def prepare_move(self, motion):
        """
        - TODO for multiple move...
        cf  ...b +  B command send to 127  ( NOT TO DO for now )
        """
        pass

    def start_one(self, motion):
        """
        'T': absolute movement in closed-loop mode.

        NB: "JXX,YY,ZZZ" : relative movement in open-loop
            to use with motion.delta
        """
        absolute_target_pos = int(motion.target_pos)

        self.send(motion.axis, f"T{absolute_target_pos}")

    def stop(self, axis):
        """
        'S': Stop axis motion
        """
        self.send(axis, "C0")
        self.send(axis, "S")

    def state(self, axis):
        """
        Compute axis state based on status.
        0088 -> parked + servoMode
        """
        self.update_status(axis)
        status_value = self.axis_status[axis]

        if self.is_parked(status_value):
            return AxisState("OFF")

        # running means position is corrected, related to closed loop
        # we just check if target position was reached
        if self.is_closed_loop(status_value):
            if self.is_position_reached(status_value):
                return AxisState("READY")
            else:
                return AxisState("MOVING")
        else:
            if self.is_moving(status_value):
                return AxisState("MOVING")
            else:
                return AxisState("READY")

    def status(self, axis):
        """
        Return a string composed by controller and motor status string.
        """
        return "ttt"

    @object_method(types_info=("None", "string"))
    def get_info(self, axis):
        """
        Return a string of info to display to user.
        """
        info_list = [
            ("Info               ", "?"),
            ("Target mode parameters, Y2...Y13   ", "Y30"),
            (
                "Controller status U2:{5V},{3.3V},{48V},{M23},{Temp},{s5V}             ",
                "U2",
            ),
            ("Controller status U3:{cap},{freq}            ", "U3"),
            ("Controller status U4:{d1}{d2}{d3}{d4},{out}{in}            ", "U4"),
        ]

        info_str = ""

        # ???
        self.update_status(axis)

        for iii in info_list:
            info_str += "    %s %s\n" % (iii[0], self.send(axis, iii[1]))

        return info_str

    # ===== PMD301 commands

    def park_motor(self, axis):
        """
        Parks axis motor.
        """
        self.send(axis, "M4")

    def unpark_motor(self, axis):
        """
        Unpark axis motor (mandatory before moving).
        + power ON in "Rhomb mode"
        """
        self.send(axis, "M1")

    def closed_loop_reset_error(self, axis):
        self.send(axis, "C0")

    # ===== PMD301 status

    def update_status(self, axis):
        """
        Sends status command (U0) and puts results in :
        - self.ctrl_status
        - self.axis_status[axis]  (int)
        """
        ans = self.send(axis, "U0")
        status = int(ans, 16)  # decode hexa. ex: "0092" -> 146
        self.axis_status[axis] = status
        # self.ctrl_status = ???

    def is_moving(self, status):
        return status & 0x0001

    def is_closed_loop(self, status):
        return status & 0x0020

    def is_servo_mode(self, status):
        return status & 0x0080

    def is_position_reached(self, status):
        return status & 0x0010

    def is_parked(self, status):
        return status & 0x0008

    #    def get_controller_status(self):
    #        """
    #        Return a string build with all status of controller.
    #        """
    #        _s = hex_to_int(self._ctrl_status)
    #        _status = ""
    #
    #        for _c in self._controller_error_codes:
    #            if _s & _c[0]:
    #                # print _c[1]
    #                _status = _status + (_c[1] + "\n")
    #
    #        return _status

    def get_motor_status(self, axis):
        """
        Return a string build with all status of motor <axis>.
        """
        self.update_status(axis)
        status_val = self.axis_status[axis]
        status_str = f"0x{status_val:04x} : "

        if status_val & 0x0001:
            status_str += "running "
        if status_val & 0x0002:
            status_str += "reverse "
        if status_val & 0x0004:
            status_str += "overheat "
        if status_val & 0x0008:
            status_str += "parked "

        if status_val & 0x0010:
            status_str += "targetReached "
        if status_val & 0x0020:
            status_str += "targetMode "
        if status_val & 0x0040:
            status_str += "targetLimit "
        if status_val & 0x0080:
            status_str += "servoMode "

        if status_val & 0x0100:
            status_str += "index "
        if status_val & 0x0200:
            status_str += "script "
        if status_val & 0x0400:
            status_str += "xLimit "
        if status_val & 0x0800:
            status_str += "reset "

        if status_val & 0x1000:
            status_str += "cmdError "
        if status_val & 0x2000:
            status_str += "voltageError "
        if status_val & 0x4000:
            status_str += "encError "
        if status_val & 0x8000:
            status_str += "comError "

        return status_str

    # ===== PMD301 communication

    def send(self, axis, cmd):
        """
        Build command to send to controller.
        Treat answer if any.

        - Add 'X<chan_number>' prefix
        - Add the 'carriage return' terminator character : "\\\\r"
        - Encode command
        - Send command to the PMD301 controller.
        - if <axis> is 0 : send a broadcast message.
        """
        # Sanitize cmd (no LF CR)
        cmd = cmd.strip()
        if "\r" in cmd:
            log_error(self, "forbidden CR in cmd=%r", cmd)
        if "\n" in cmd:
            log_error(self, "forbidden LF in cmd=%r", cmd)
        if len(cmd) > 42:
            log_error(self, "too long (>42) cmd=%r", cmd)

        # Forge
        command = f"X{axis.chan_number}{cmd}"

        # Lock to not mix channels communications ?
        with self.lock:

            ans = self.sock.write_readline(
                f"{command}\r".encode(), eol="\r", timeout=3
            ).decode()

            if (
                self._isHalfDuplex
            ):  # This is the case when half-duplex is connected to full duplex device server (brainbox)
                command = ans
                ans = self.sock.readline(eol="\r", timeout=3).decode()

            ans = f"{command}\r{ans}"
            ans_fields = ans.split("\r")

            try:
                cmd_chk, cmd_ans = ans_fields[1].split(":")
                if (
                    cmd_chk != f"X{axis.chan_number}{cmd}"
                    and cmd_chk != f"X{axis.chan_number}{cmd[:-1]}"
                ):
                    log_error(self, "PMD301 ERROR: cmd_chk=%r", cmd_chk)

            except ValueError:
                # no ':' => cmd was not a query ?
                # always got a '!' in the answer ?
                if ans_fields[0] + "!" == ans_fields[1]:
                    log_error(self, "PMD301 ERROR: %r", command)
                    cmd_ans = None
                elif ans_fields[0] == ans_fields[1]:
                    log_debug(self, "PMD301: ok command well executed ")
                    cmd_ans = None
                else:
                    log_debug(
                        self,
                        "PMD301 ERROR: cmd '%r' not well executed ? (recv=%r)",
                        command,
                        ans,
                    )
                    cmd_ans = None

            return cmd_ans

    # TESTED Commands:
    # get model       ?   -> 'X1?\rX1?:PMD301 V26\r' -> 'PMD301 V26'
    #                 T   -> 'X1T\rX1T:0\r' -> '0'
    #                 E   -> 'X1E\rX1E:0\r' -> '0'
    # axis status     U0  -> 'X1U0\rX1U0:0088\r' -> '0088' ->
    #                 U1  -> 'X1U1\rX1U1:21\r'   -> '21'   ->
    #                 U2  -> 'X1U2\rX1U2:3.31,4.96,48.4,23,31C,5\r' -> '3.31,4.96,48.3,23,31C,5' -> ?
    #                 U3  -> 'X1U3\rX1U3:0nF,0Hz Delta\r' -> '0nF,0Hz Delta' -> ?
    #                 U4  -> 'X1U4\rX1U4:0088,21\r' -> '0088,21' ( = U0 + U1 ?)

    # move            T10 -> 'X1T10\rX1T10!\r'     # no ':'

    # ??? : Y30
    # init serial encoder : Y13
    # time to reach target ? : Y23
    # park motor / power down : M4

    # X?   (without axis number) does not work

    def get_error(self, axis):
        pass

    def _raw_write_read(self, raw_cmd):
        """
        write / read raw cmd
        <raw_cmd> : bytes
        """
        self.sock.write(raw_cmd)
        return self.sock.raw_read()

    """
    Raw write read commands for tango DS
    """

    @object_method(types_info=("String", "String"))
    def raw_write_read(self, cmd):
        return self.sock.write_readline(f"{cmd}\r".encode(), eol="\r").decode()

    def raw_write_read_axis(self, axis, cmd):
        return self.send(axis, cmd)
