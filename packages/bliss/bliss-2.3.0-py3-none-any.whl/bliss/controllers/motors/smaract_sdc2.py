# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""SmarAct SDCS2 motor controller

SDC2 only.
MCS2 -> see smaract_mcs2.py
MCS -> see smaract.py


Control via serial line rs232


There are two steps size in config:

 steps_per_unit: 1e6  # usual one
 smaract_steps: 3100  # for movement MST command

"""

from datetime import datetime

from bliss.common.axis import AxisState
from bliss.comm.util import get_comm
from bliss.controllers.motor import Controller


def timestamp_hour_us():
    """
    Timestamp string
    * with blank space
    * with micro second accuracy
    """
    return datetime.now().strftime("%H:%M:%S.%f")


def print_sdc2(msg):
    print(f"[{timestamp_hour_us()}] [SDC2] {msg}")


class SmarActError(Exception):

    ERRORS = {
        0: "No error",
        1: "Syntax Error",
        2: "Invalid Command",
        3: "Overflow",
        4: "Parse Error",
        5: "Too Few Parameters",
        6: "Too Many Parameters",
        7: "Invalid Parameter",
        8: "Wrong Mode",
        129: "No Sensor Present",
        140: "Sensor Disabled",
        141: "Command Overridden",
        142: "End Stop Reached",
        143: "Wrong Sensor Type",
        144: "Could Not Find Reference Mark",
        145: "Wrong End Effector Type",
        146: "Movement Locked",
        147: "Range Limit Reached",
        148: "Physical Position Unknown",
        150: "Command Not Processable",
        151: "Waiting For Trigger",
        152: "Command Not Triggerable",
        153: "Command Queue Full",
        154: "Invalid Component",
        155: "Invalid Sub Component",
        156: "Invalid Property",
        157: "Permission Denied",
        159: "Power Amplifier Disabled",
        160: "Calibration Failed",
        161: "Incomplete Packet",
        162: "Initialization Failed",
        # 0    : "No Error This indicates that no error occurred and therefore corresponds to an acknowledge. "
        # 1    : "Syntax Error The command could not be processed due to a syntactical error. "
        # 2    : "Invalid Command Error The command given is not known to the system. "
        # 3    : "Overflow Error This error occurs if a parameter given is too large and therefore cannot be processed. "
        # 4    : "Parse Error The command could not be processed due to a parse error. "
        # 5    : "Too Few Parameters Error The specified command requires more parameters in order to be executed. "
        # 6    : "Too Many Parameters Error There were too many parameters given for the specified command. "
        # 7    : "Invalid Parameter Error A parameter given exceeds the valid range. Please see the command description for valid ranges of the parameters. "
        # 129  : "No Sensor Present Error This error occurs if a command was given that requires sensor feedback, but the positioner has none attached. "
        # 142  : "End Stop Reached Error This error is generated if the target position of a closed-loop command could not be reached, because a mechanical end stop was detected. "
        # 144  : "Could Not Find Reference Mark Error This error is generated if the search for a reference mark was aborted. See section 2.2.3 “Reference Marks” for more information. "
        # 150  : "Command Not Processable Error This error is generated if a command is sent to the module when it is in a state where the command cannot be processed. For example, to start the find reference mark sequence the positioner must be calibrated. In this case send a calibrate command before. "
        # 159  : "Power Amplifier Disabled Error This error is returned if a movement command (e.g. CS, FRM, MST) was given while the power amplifier is disabled. (ON/OFF mode configured to “high voltage” and ON/OFF signal line in low state) "
        # 160  : "Calibration Failed Error This error is generated if the calibration routine was started (the ascii command CS was received or the calibration button on the controller board was pressed) and could not finish for some reason, e.g. an endstop was reached. "
        # 161  : "Incomplete Packet Error This error is generated if a command string was not received completely and a timeout occures. "
        # 162  : "Initialization Failed Error This error is generated if an internal error occurred. "
    }

    def __init__(self, code, channel=-1):
        try:
            code = int(code)
            msg = self.ERRORS.setdefault(code, "Unknown error")
        except ValueError:
            msg = code
            code = -1000
        channel = int(channel)
        if channel == -1:
            msg = "Error {}: {}".format(code, msg)
        else:
            msg = "Error {} on channel {}: {}".format(code, channel, msg)
        super(SmarActError, self).__init__(msg)


def parse_reply_item(reply):
    try:
        return int(reply)
    except ValueError:
        try:
            return float(reply)
        except ValueError:
            return reply


def parse_reply(reply, cmd):
    if reply.startswith(":E"):
        channel, code = map(int, reply[2:].split(",", 1))
        if code:
            raise SmarActError(code, channel)
        return 0
    else:
        # we are in a get command for sure
        is_channel_cmd = True
        try:
            # limitation: fails if controller has more that 10 channels
            int(cmd[-1])
        except ValueError:
            is_channel_cmd = False
        if is_channel_cmd:
            reply = reply.split(",", 1)[1]
        else:
            # strip ':' + cmd name so all is left is reply
            reply = reply[len(cmd) + 1 :]
        if "," in reply:
            data = [parse_reply_item(item) for item in reply.split(",")]
        else:
            data = parse_reply_item(reply)
        return data


class SmaractSDC2(Controller):

    """
    Devel notes:

    .. code-block::

        GCM  -> :CM0               0 for synchronous communication or 1 for asynchronous communication. (should be 0)
        GIV  -> :IV1,1,0,56        IV<versionHigh>,<versionLow>,<versionUpdate>
        GNC  -> :N1                1 channel
        GSI  -> :IDSDC2 82056198   generic decimal number that uniquely identifies the system.
        GTP  -> :TP0,9359          get target position
        GST  -> :ST0,21'           encoder type 21

        GS0  -> :S0,3              get status 3 : holding target or reference pos
        R : reset
        GSD -> :SD0,0              Requests the safe direction that is currently configured for channel 0

        MST0,-1000,4095,1000      burst of steps ??? (move -1000 steps, with maximum amplitude = 4095, at 1000 Hz)

        While executing the command the positioner will have a movement status code of 4. While holding the target
        position the positioner will have a movement status code of 3 (see GS command).

        :FRM0,0,2000,1  ->        Homing  positive direction hold 2s set 0 at ref

        GES -> :ES0,161,2'

        GTE0,0,0 ->  :SI0,0,1

    """

    def initialize(self):
        """ """
        print_sdc2(f"initialize({self.name})")
        self.comm = get_comm(self.config.config_dict)

        self.smaract_steps = self.config.get("smaract_steps")
        # 3100  # 1 step = 2.6 um  for  MST command, changed for 2.9um on 3 sep 2025

    def initialize_hardware(self):
        """ """
        print_sdc2(f"initialize_hardware({self.name})")
        # set communication mode to synchronous

    #        self["CM"] = 0
    #        self.sensor_enabled = self.config.get(
    #            "sensor_enabled", default=SensorEnabled.Enabled
    #        )

    def initialize_axis(self, axis):
        """ """
        print_sdc2(f"initialize_axis({axis.name})")
        axis.axis_channel = axis.config.get("axis_channel", int)

        # if "hold_time" in axis.config.config_dict:
        #    axis.channel.hold_time = axis.config.get("hold_time", float)

    def get_axis_info(self, axis):
        """
        Return controller-specific info about <axis>.
        """
        info_str = f"   smaract_steps: {self.smaract_steps}\n"

        return info_str

    def send(self, command):
        """
        <command> (str): command to send.
        ex : GP0

        * forge request with given command
        * add terminator
        * encode
        * send
        * read reply
        * decode
        """

        # TODO: purge command : ex : remove ":" ? or error ?

        request = f":{command}\n"

        replyb = self.comm.write_readline(request.encode())
        print_sdc2(f"SEND:{command}  RECV:{replyb}")

        reply = replyb.decode()

        if reply.startswith(":E"):
            _msg = "ERROR\n"
            _msg += f"Command was '{command}'\n"
            _msg += f"Reply is '{reply}'\n"
            _err_no = int(reply.split(",")[1])

            raise SmarActError(_err_no)

        return reply

    def state(self, axis):
        """ """

        _cmd = f"GS{axis.axis_channel}"
        _read_status = self.send(_cmd)
        _status_number = parse_reply(_read_status, _cmd)

        if _status_number == 1:
            return AxisState("MOVING")

        if _status_number == 3:
            return AxisState("READY")

        print_sdc2(f"_status_number = {_status_number} -> UNNK")
        return AxisState("UNKNONW")

    def stop(self, axis):
        """
        S0 command
        """
        _channel = axis.axis_channel
        self.send(f"S{_channel}")

    #        if not axis.channel.status == ChannelStatus.FindingReferenceMark:
    #            axis.channel.stop()
    #        else:
    #            self.command("S")
    #        log_debug(self, "{0} sent stop".format(axis.name))

    def set_on(self, axis):
        """ """
        print("set_on NOT implemented")

    def set_off(self, axis):
        """ """
        print("set_off NOT implemented")

    def set_position(self, axis, pos):
        """ """
        print("set_position NOT IMPLEMENTED")

    def read_position(self, axis):
        """
        Use GP0 command

        Return: steps

        """
        channel = axis.axis_channel
        cmd = f"GP{channel}"
        ans = self.send(cmd)

        steps_encoder = parse_reply(ans, cmd)  # 1 nano-meter / step

        return steps_encoder

    def start_one(self, motion):
        """
        Use MST command
        NB: only integer number of steps.
        """
        channel = motion.axis.axis_channel
        relative_move = motion.delta  # nm

        nb_steps = int(relative_move / self.smaract_steps)

        # How theses value have to be tuned ?
        # TODO: to put in config or setting ?
        amplitude = 4095
        freq = 1000

        cmd = f"MST{channel},{nb_steps},{amplitude},{freq}"
        ans = self.send(cmd)
        print_sdc2(f"---- ans start={ans}")

    def read_velocity(self, axis):
        return 0.5

    def set_velocity(self, axis, new_velocity):
        return 0.5

    def read_acceleration(self, axis):
        return 1

    def set_acceleration(self, axis, new_acceleration):
        return 1
