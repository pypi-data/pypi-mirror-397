# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import time
import gevent
from gevent.event import AsyncResult
from gevent.lock import Semaphore
from gevent.queue import Queue, Empty

from warnings import warn
from dataclasses import dataclass, field
from bliss.controllers.motor import Controller
from bliss.config.settings import QueueSetting
from bliss.common.utils import object_method
from bliss.common.axis import AxisState, CyclicTrajectory
from bliss.common.logtools import log_error, log_debug
from bliss.comm.util import get_comm
from bliss.comm.serial import SerialTimeout
from bliss.comm.exceptions import CommunicationError
from bliss import global_map


MAX_VELOCITY = 400000
MIN_VELOCITY = 1
MAX_ACCELERATION = 400000
MIN_ACCELERATION = 1
MAX_DECELERATION = 400000
MIN_DECELERATION = 1
MAX_CREEP_SPEED = 1000
MIN_CREEP_SPEED = 1

# Status bits: abcdefgh
# a is 0 = Busy or 1 = Idle
# b is 0 = OK   or 1 = Error (abort, tracking, stall, timeout etc.)
# c is 0 = Upper hard limit is OFF or 1 = Upper hard limit is ON
# d is 0 = Lower hard limit is OFF or 1 = Lower hard limit is ON
# e is 0 = Not jogging or joystick moving or 1 = Jogging or joystick moving
# f is 0 = Not at datum sensor point or 1 = On datum sensor point
# g is 0 = Future use or 1 = Future use
# h is 0 = Future use or 1 = Future use
ST_IDLE = 0b10000000
ST_ERROR = 0b01000000
ST_LIMPOS = 0b00100000
ST_LIMNEG = 0b00010000
ST_JOG = 0b00001000
ST_DAT = 0b00000100

"""
Bliss controller for McLennan PM600/PM1000 motor controller.

"""


@dataclass
class PM600Command:
    message: bytes
    expected_replies: int
    result: AsyncResult = field(default_factory=AsyncResult)


@dataclass
class PM600Echo:
    message: bytes
    sending_time: float


class PM600(Controller):
    def __init__(self, *args, **kwargs):
        Controller.__init__(self, *args, **kwargs)
        self._reading_task = None
        self._cmd_lock = Semaphore()
        self._cmd_queue = Queue()
        self._echo_queue = Queue()

    def steps_position_precision(self, axis):
        return self.config.config_dict.get("precision", 1)

    def initialize(self):
        try:
            self.sock = get_comm(self.config.config_dict)
        except ValueError:
            host = self.config.get("host")
            port = int(self.config.get("port"))
            warn(
                "'host' and 'port' keywords are deprecated. " "Use 'tcp' instead",
                DeprecationWarning,
            )
            comm_cfg = {"tcp": {"url": "{0}:{1}".format(host, port)}}
            self.sock = get_comm(comm_cfg)

        global_map.register(self, children_list=[self.sock])

    def finalize(self):
        self.sock.close()

    def initialize_hardware(self):
        # read spurious 'd' character when connected
        # on ID26, via Serial, there is no spurious character to be read ...
        try:
            self.sock.readline(eol="\r")
        except CommunicationError:
            pass

    # Initialize each axis.
    def initialize_hardware_axis(self, axis):

        # Set velocity feedforward on axis
        self.io_command("KF", axis.channel, axis.kf)
        # Set the proportional gain on axis
        self.io_command("KP", axis.channel, axis.kp)
        # Set the Sum gain on axis
        self.io_command("KS", axis.channel, axis.ks)
        # Set the Velocity feedback on axis
        self.io_command("KV", axis.channel, axis.kv)
        # Set the Extra Velocity feedback on axis
        self.io_command("KX", axis.channel, axis.kx)
        # Set slew rate of axis (steps/sec)
        """
        self.io_command("SV", axis.channel, int(axis.slewrate))
        # Set acceleration of axis (steps/sec/sec)
        self.io_command("SA", axis.channel, int(axis.accel))
        """
        # Set deceleration of axis (steps/sec/sec)
        self.io_command("SD", axis.channel, axis.decel)
        # Set creep speed of axis (steps/sec/sec)
        self.io_command("SC", axis.channel, axis.creep_speed)
        # Set number of creep steps at the end of a move (steps)
        self.io_command("CR", axis.channel, axis.creep_steps)
        # Set the deceleration rate for stopping when hitting a Hard Limit or a Soft Limit
        self.io_command("LD", axis.channel, axis.limit_decel)
        # Set settling time (milliseconds)
        self.io_command("SE", axis.channel, axis.settling_time)
        # Set the Set the Window for axis (steps)
        self.io_command("WI", axis.channel, axis.window)
        # Set the threshold before motor stalled condition (%)
        self.io_command("TH", axis.channel, axis.threshold)
        # Set the tracking window of the axis (steps)
        self.io_command("TR", axis.channel, axis.tracking)
        # Set the axis time out (millisecond)
        self.io_command("TO", axis.channel, axis.timeout)
        # Sets the soft limits (enable = 1, disable = 0)
        self.io_command("SL", axis.channel, axis.soft_limit_enable)
        if axis.soft_limit_enable == 1:
            # Set the axis upper soft limit position (steps)
            self.io_command("UL", axis.channel, axis.high_steps)
            # Set the axis lower soft limit position (steps)
            self.io_command("LL", axis.channel, axis.low_steps)
        # Set encoder ratio
        cmd = "ER{0}/{1}".format(
            axis.encoder_ratio_numerator, axis.encoder_ratio_denominator
        )
        self.io_command(cmd, axis.channel)
        # Set gearbox ratio numerator
        self.io_command("GN", axis.channel, axis.gearbox_ratio_numerator)
        # Set gearbox ratio denominator
        self.io_command("GD", axis.channel, axis.gearbox_ratio_denominator)

    def initialize_axis(self, axis):
        axis.channel = axis.config.get("address")
        self.channel = axis.channel

        axis.kf = axis.config.get("Kf", int, default=0)
        axis.kp = axis.config.get("Kp", int, default=10)
        axis.ks = axis.config.get("Ks", int, default=0)
        axis.kv = axis.config.get("Kv", int, default=0)
        axis.kx = axis.config.get("Kx", int)
        axis.slewrate = axis.config.get("velocity", float, default=1000.0)
        axis.accel = axis.config.get("acceleration", float, default=2000.0)
        axis.decel = axis.config.get("deceleration", int, default=3000)
        axis.creep_speed = axis.config.get("creep_speed", int, default=800)
        axis.creep_steps = axis.config.get("creep_steps", int, default=0)
        axis.limit_decel = axis.config.get("limit_decel", int, default=2000000)
        axis.settling_time = axis.config.get("settling_time", int, default=100)
        axis.window = axis.config.get("window", int, default=4)
        axis.threshold = axis.config.get("threshold", int, default=50)
        axis.tracking = axis.config.get("tracking", int, default=4000)
        axis.timeout = axis.config.get("timeout", int, default=8000)
        axis.soft_limit_enable = axis.config.get("soft_limit_enable", int, default=1)
        axis.low_steps = axis.config.get("low_steps", float, default=-2000000000)
        axis.high_steps = axis.config.get("high_steps", float, default=2000000000)
        axis.gearbox_ratio_numerator = axis.config.get(
            "gearbox_ratio_numerator", int, default=1
        )
        axis.gearbox_ratio_denominator = axis.config.get(
            "gearbox_ratio_denominator", int, default=1
        )
        axis.encoder_ratio_numerator = axis.config.get(
            "encoder_ratio_numerator", int, default=1
        )
        axis.encoder_ratio_denominator = axis.config.get(
            "encoder_ratio_denominator", int, default=1
        )
        axis.trajectory_profile_number = axis.config.get(
            "profile_number", int, default=0
        )
        axis.trajectory_sequence_number = axis.config.get(
            "sequence_number", int, default=2
        )
        axis.trajectory_pre_xp = axis.config.get("pre_xp", list, default=[])
        axis.trajectory_post_xp = axis.config.get("post_xp", list, default=[])

        axis.trajectory_prog = QueueSetting("{0}.trajectory_prog".format(axis.name))

    def finalize_axis(self):
        pass

    def initialize_encoder(self, encoder):
        encoder.channel = encoder.config.get("address")

    def read_position(self, axis):
        reply = self.io_command("OC", axis.channel)
        return float(reply)

    def read_encoder(self, encoder):
        return float(self.io_command("OA", encoder.channel))

    def read_acceleration(self, axis):
        reply = self.io_command("QS", axis.channel)
        tokens = reply.split()
        return float(tokens[8])

    def read_deceleration(self, axis):
        reply = self.io_command("QS", axis.channel)
        tokens = reply.split()
        return int(tokens[11])

    def read_velocity(self, axis):
        reply = self.io_command("QS", axis.channel)
        return float(reply.split()[5])

    def read_firstvelocity(self, axis):
        reply = self.io_command("QS", axis.channel)
        tokens = reply.split()
        return int(tokens[2])

    def set_velocity(self, axis, velocity):
        if velocity > MAX_VELOCITY or velocity < MIN_VELOCITY:
            log_error(self, "velocity out of range: {0}".format(velocity))
        reply = self.io_command("SV", axis.channel, velocity)
        if reply != "OK":
            log_error(self, "unexpected response to set_velocity" + reply)

    def set_firstvelocity(self, axis, creep_speed):
        if creep_speed > MAX_CREEP_SPEED or creep_speed < MIN_CREEP_SPEED:
            log_error(self, "creep_speed out of range")
        reply = self.io_command("SC", axis.channel, creep_speed)
        if reply != "OK":
            log_error(self, "Unexpected response to set_firstvelocity" + reply)

    def set_acceleration(self, axis, acceleration):
        if acceleration > MAX_ACCELERATION or acceleration < MIN_ACCELERATION:
            log_error(self, "acceleration out of range")
        reply = self.io_command("SA", axis.channel, acceleration)
        if reply != "OK":
            log_error(self, "Unexpected response to set_acceleration" + reply)

    def set_decel(self, axis, deceleration):
        if deceleration > MAX_DECELERATION or deceleration < MIN_DECELERATION:
            log_error(self, "deceleration out of range")
        reply = self.io_command("SD", axis.channel, deceleration)
        if reply != "OK":
            log_error(self, "Unexpected response to set_deceleration" + reply)

    def set_position(self, axis, position):
        reply = self.io_command("AP", axis.channel, position)
        if reply != "OK":
            log_error(self, "Unexpected response to set_position" + reply)
        return self.read_position(axis)

    def state(self, axis):
        """
        Return interpretation of status
        """
        status = self.status(axis)
        if status & ST_ERROR:
            return AxisState("FAULT")
        elif not status & ST_IDLE:
            return AxisState("MOVING")
        elif status & ST_LIMPOS:
            return AxisState("LIMPOS")
        elif status & ST_LIMNEG:
            return AxisState("LIMNEG")
        else:
            return AxisState("READY")

    def prepare_move(self, motion):
        pass

    def start_one(self, motion):
        reply = self.io_command("MA", motion.axis.channel, int(motion.target_pos))
        if reply != "OK":
            log_error(self, "Unexpected response to move absolute" + reply)

    def stop(self, motion):
        reply = self.io_command("ST", motion.axis.channel)
        if reply != "OK":
            log_error(self, "Unexpected response to stop" + reply)
        # status = self.status(motion.axis)
        # if status[0:1] == "0":
        #    reply = self.io_command("ST", motion.axis.channel)
        #    if reply != "OK":
        #        log_error(self, "Unexpected response to stop" + reply)

    def start_all(self, *motion_list):
        for motion in motion_list:
            self.start_one(motion)

    def stop_all(self, *motion_list):
        for motion in motion_list:
            self.stop(motion)

    def home_search(self, axis, switch):
        reply = self.io_command("DM00100000", axis.channel)
        if reply != "OK":
            log_error(self, "Unexpected response to datum mode" + reply)
        reply = self.io_command("HD", axis.channel, (+1 if switch > 0 else -1))
        if reply != "OK":
            log_error(self, "Unexpected response to home to datum" + reply)

    def home_state(self, axis):
        return self.state(axis)

    def get_axis_info(self, axis):
        return self.io_command("QA", axis.channel, nreplies=23)

    def _check_error(self, reply):
        if reply.startswith("!"):
            raise Exception(f"PM600 Error: {reply[1:]}")
        return reply

    def _halt(self, soft=False):
        """Halt motion, reset command buffer on device and resync.
        Not a kill-safe method, should be ran in background."""
        stop_char = b"\x1b" if soft else b"\x03"
        with self._cmd_lock:
            if self._reading_task is not None:
                self._reading_task.kill()  # blocking

            # send stop_char + wait echo to resync with the PM600
            if self.sock._raw_handler is not None:  # aka .is_open()
                try:
                    self.sock._raw_handler.write(stop_char, timeout=1.0)
                    discarded = self.sock._raw_handler.readline(
                        eol=stop_char, timeout=1.0
                    )
                    log_debug(
                        self, "Stop character sent, discarded RX buffer: %s", discarded
                    )
                except SerialTimeout:
                    log_error(self, "Communication resync timed out")
                    self.sock.close()
                    raise

            # no need to restart a reading task, it is spawned when needed

    def _list_query(self, cmd_name: str, channel: int, profile_id: int):
        """For LP, LS and LC commands, aka the commands with unpredictible
        response size.
        Should not be interrupted (to be called in a greenlet)"""
        while True:
            with self._cmd_lock:
                if self._reading_task is not None:
                    try:
                        # wait for the reading task to stop by itself,
                        # but regularly release the lock to let an halt
                        # request to overtake.
                        self._reading_task.join(timeout=0.1)
                    except gevent.Timeout:
                        continue

                command = f"{channel}{cmd_name}{profile_id}\r".encode()
                self.sock.write(command)
                resp = b""
                while True:
                    try:
                        resp += self.sock._raw_handler.raw_read(timeout=0.5, maxsize=0)
                    except SerialTimeout:
                        # request is complete after some time without new chars
                        break

                lines = resp[:-2].split(b"\r\n")
                echo, _, lines[0] = lines[0].partition(b"\r")
                echo += b"\r"
                if echo != command:
                    raise Exception(f"Expected echo {command}, got {echo}")
                return lines

    def _submit_command(
        self, message: bytes, expected_replies: int = 1, wait: bool = True
    ):
        with self._cmd_lock:
            command = PM600Command(message, expected_replies)
            echo = PM600Echo(message, time.perf_counter())
            self._cmd_queue.put(command)
            self._echo_queue.put(echo)
            self.sock.write(message)

            if self._reading_task is None:
                self._reading_task = gevent.spawn(self._reading_loop)
                self._reading_task.link_exception(self._reading_loop_error)

        if wait:
            return command.result.get()

    def _reading_loop_error(self, greenlet):
        log_error(self, "_reading_loop failed: %s", str(greenlet.exception))

    @staticmethod
    def _filter_echo(data: bytes, echo: bytes) -> bytes:
        """Return a filtered version of data if echo is found with at most one
        interleaved character. Raise ValueError otherwise.
        Example:
            data: b"12a3bc456789"
            echo: b"abc"
            return: b"123456789"
            # a single character sits in the middle of 'abc', which is tolerated.
        """
        start = data.find(echo[0])
        while start != -1:
            filtered = data[:start]
            missed = 0
            echo_pos = 0
            for c in data[start:]:
                if echo_pos == len(echo):  # echo is already matched
                    filtered += chr(c).encode()
                elif c == echo[echo_pos]:
                    echo_pos += 1
                    # missed = 0 # reset missed to authorize non-echo chars between each echo char
                elif missed < 1:  # number of non-echo chars tolerated within echo
                    filtered += chr(c).encode()
                    missed += 1
                else:
                    # too much difference with the expected echo
                    break
            if echo_pos == len(echo):
                return filtered
            start = data.find(echo[0], start + 1)
        raise ValueError("Echo not found")

    def _reading_loop(self):
        replies = []
        buffer = b""
        while not self._cmd_queue.empty():
            try:
                # killing reading loop occurs in this try/except
                # its only processing outside there
                while True:
                    try:
                        buffer += self.sock._raw_handler.raw_read(
                            maxsize=0, timeout=0.2
                        )
                        break
                    except SerialTimeout:
                        pass

                    # ensure pending echos are not getting too old
                    try:
                        pending_echo = self._echo_queue.peek_nowait()
                    except Empty:
                        pass
                    else:
                        if time.perf_counter() > pending_echo.sending_time + 3.0:
                            raise Exception(
                                f"No echo received for {pending_echo.message} after three seconds (normally takes ~10ms)"
                            )
            except BaseException:
                # purge queues with sentinel values
                self._cmd_queue.put(StopIteration)
                self._echo_queue.put(StopIteration)
                for cmd in self._cmd_queue:
                    # tell everyone its command is aborted
                    cmd.result.set_exception(
                        Exception(f"Command {cmd.message} aborted")
                    )
                _ = list(self._echo_queue)

                self._reading_task = None
                raise

            # clear all pending echos before looking at replies
            while not self._echo_queue.empty():
                echo = self._echo_queue.peek_nowait()
                try:
                    buffer = PM600._filter_echo(buffer, echo.message)
                    _ = self._echo_queue.get_nowait()
                except ValueError:
                    break
            if not self._echo_queue.empty():
                # not all echos are received, back to reading...
                continue

            parts = buffer.split(b"\r\n")
            replies += parts[:-1]
            buffer = parts[-1]

            while replies:
                expected_replies = self._cmd_queue.peek_nowait().expected_replies
                if b"!" in replies[0]:
                    self._cmd_queue.get_nowait().result.set(replies.pop(0))
                elif len(replies) >= expected_replies:
                    self._cmd_queue.get_nowait().result.set(replies[:expected_replies])
                    replies = replies[expected_replies:]
                else:
                    break

        self._reading_task = None

    def io_command(
        self, command, channel, value=None, nreplies=1, programming=False, wait=True
    ):
        cmd = f"{channel}{command}{value if value is not None else ''}\r"
        replies = self._submit_command(cmd.encode(), nreplies, wait=wait)
        if wait:
            if nreplies == 1 and not programming:
                reply = replies[0].decode()
                channel, value = reply.split(":")
                self._check_error(value)
                return value
            else:
                return "\n".join([self._check_error(rep.decode()) for rep in replies])

    """
    PM600 added commands
    """

    @object_method(types_info=("None", "int"))
    def status(self, axis):
        """
        Return raw status value (bit field)
        """
        # convert to int (binary field)
        return int(self.io_command("OS", axis.channel), 2)

    @object_method(types_info=("None", "int"))
    def get_id(self, axis):
        """
        This command is used to give the type of controller
        and its internal software revision.
        """
        return self.io_command("ID", axis.channel)

    @object_method(types_info=("None", "None"))
    def abort(self, axis):
        """
        The control of the motor is aborted.
        A user abort may be reset with the 'reset' command
        """
        self.io_command("AB", axis.channel)

    @object_method(types_info=("None", "None"))
    def reset(self, axis):
        """
        This command will reset the tracking abort, stall abort,
        time out abort or user(command) abort conditions and
        re-enable the servo control loop. It will also set the
        Command position to be equal to the Actual position.
        It also clears trajectory_prog.
        """
        self.io_command("RS", axis.channel)
        axis.trajectory_prog.clear()

    @object_method(types_info=("None", "float"))
    def get_deceleration(self, axis):
        return self.read_deceleration(axis)

    @object_method(types_info=("float", "None"))
    def set_deceleration(self, axis, deceleration):
        return self.set_decel(axis, deceleration)

    #
    # Trajectories
    #

    def has_trajectory(self):
        return True

    def prepare_trajectory(self, *trajectories):
        if not trajectories:
            raise ValueError("PM600: no trajectory provided")

        # Can define up to 8 profiles from DP0 to DP7
        #             and 8 sequences from DS0 to DS7

        for traj in trajectories:

            is_cyclic_traj = isinstance(traj, CyclicTrajectory)

            channel = traj.axis.channel
            prf_num = traj.axis.trajectory_profile_number
            seq_num = traj.axis.trajectory_sequence_number
            pre_xp = traj.axis.trajectory_pre_xp
            post_xp = traj.axis.trajectory_post_xp

            time = traj.pvt["time"]
            positions = traj.pvt["position"]

            if len(time) < 2:
                log_debug(self, "trajectory is empty: {0}".format(positions))
                raise ValueError(
                    "PM600: Wrong trajectory provided, need at leat 2 lines PVT"
                )

            ncycles = traj.nb_cycles if is_cyclic_traj else 1
            nsteps = (len(positions) - 1) * ncycles + (ncycles - 1)
            if nsteps > 127:
                raise RuntimeError(
                    "PM600: Too many profile steps {0} (maxi: 127)".format(nsteps * 4)
                )

            t1 = time[1:] - time[: time.size - 1]
            tstep = t1.mean()
            if tstep != t1[0]:
                raise RuntimeError(
                    "PM600 controller only supports unique time value to complete each element "
                    "in a profile definition, so time scale in PVT array must be linear."
                )

            if tstep * 1000 > 65635:
                raise RuntimeError(
                    "PM600: Too long time duration per profile step {0} (maxi: 65 seconds)".format(
                        tstep
                    )
                )

            if tstep * 1000 < 100:
                raise RuntimeError(
                    "PM600: Too short time duration per profile step {0} (min: 0.1 seconds)".format(
                        tstep
                    )
                )

            mr = positions[1:] - positions[: positions.size - 1]
            speed = abs(mr / tstep)
            if speed.max() > 200000:
                raise RuntimeError(
                    "PM600: Too high speed for profile {0} (maxi: 200000/step)".format(
                        speed.max()
                    )
                )

            # events_pos = traj.events_positions  # not used (yet)

            prog = [
                "US{0}".format(seq_num),  # undefine sequence
                "UP{0}".format(prf_num),  # undefine profile
            ]

            # PROFILE: commands allowed are MR, and DP/EP

            prog.append("DP{0}".format(prf_num))

            for p in mr:
                prog.append("MR{0}".format(int(p)))

            prog.append("EP{0}".format(prf_num))

            # SEQUENCE: all commands allowed, and DS/ES

            prog.append("DS{0}".format(seq_num))

            # 1PTxx time to complete each interval in a profile definition (unit is ms)
            prog.append("PT{0}".format(int(tstep * 1000)))

            for cmd in pre_xp:
                prog.append("{0}".format(cmd))

            # 1XPO execute profile
            prog.append("XP{0}".format(prf_num))

            for cmd in post_xp:
                prog.append("{0}".format(cmd))

            # 1ES2 end of seq def
            prog.append("ES{0}".format(seq_num))

            if prog != traj.axis.trajectory_prog.get():
                log_debug(self, "program ready to be loaded: {0}".format(prog))

                try:
                    for cmd in prog:
                        self.io_command(cmd[0:2], channel, cmd[2:], programming=True)
                    traj.axis.trajectory_prog.set(prog)

                except BaseException as e:  # Exception does not trap keyboardinterrupt
                    log_error(
                        self,
                        "error ({2}) while programming trajectory (while loading instruction {0}{1}) - cancel programming".format(
                            channel, cmd, e
                        ),
                    )
                    self.stop_trajectory()
                    raise e

            else:
                log_debug(self, "same program already loaded: {0}".format(prog))

    def move_to_trajectory(self, *trajectories):
        pass

    def start_trajectory(self, *trajectories):
        for t in trajectories:
            self.io_command(
                "XS",
                t.axis.channel,
                value=t.axis.trajectory_sequence_number,
                nreplies=1,
                wait=False,
            )

    def stop_trajectory(self, *trajectories):
        # execute stop request in background, then killing stop_trajectory
        # would only stop waiting for completion (no need for killmask).
        gevent.spawn(self._halt).get()

    def has_trajectory_event(self):
        return False

    def set_trajectory_events(self, *trajectories):
        pass

    def trajectory_list(self, trajectory):
        return self.trajectory_list_axis(trajectory.axis)

    def trajectory_list_axis(self, axis):
        profile = gevent.spawn(
            self._list_query, "LP", axis.channel, axis.trajectory_profile_number
        ).get()
        sequence = gevent.spawn(
            self._list_query, "LS", axis.channel, axis.trajectory_sequence_number
        ).get()

        profile = [line.decode().replace(" ", "") for line in profile[1:]]
        sequence = [line.decode().replace(" ", "") for line in sequence[1:]]

        _prog = [
            "US{0}".format(axis.trajectory_sequence_number),
            "UP{0}".format(axis.trajectory_profile_number),
            "DP{0}".format(axis.trajectory_profile_number),
        ]
        _prog += profile
        _prog += [
            "EP{0}".format(axis.trajectory_profile_number),
            "DS{0}".format(axis.trajectory_sequence_number),
        ]
        _prog += sequence
        _prog += ["ES{0}".format(axis.trajectory_sequence_number)]

        axis.trajectory_prog.set(_prog)

        return (profile, sequence)

    def trajectory_backup(self, trajectory):
        # Saves all profiles and sequences definitions to non-volatile flash-mem
        # so that they are restored at power-up.
        self.io_command("BP", trajectory.axis.channel)
        print("PM600 profiles saved")
        self.io_command("BS", trajectory.axis.channel)
        print("PM600 sequences saved")
