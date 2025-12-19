# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Cirs command-line tool to adjust position of motors with keypad.
"""

from __future__ import annotations

import numpy

from bliss.common.plot import get_flint
from bliss import current_session, global_map
from bliss.common.axis import Axis
from bliss.scanning.scan_tools import peak, get_counter

from bliss.shell.standard import umv
from bliss.shell.standard import text_block
from bliss.common.utils import (
    typecheck,
    custom_error_msg,
)


def print_help(channel_name):
    print(f"curs() - axis {channel_name}")
    print("                ← →   : move the cursor")
    print("                  p   : move cursor to peak")
    print("                  🄼   : move the motor to cursor position")
    print("          esc 🅀  🅇  ⏎ : Quit without moving")
    print("               ? 🄷    : Help")
    print("")


def _get_axis_by_name(name: str) -> Axis:
    axes = list(global_map.get_axis_objects_iter(name))
    if len(axes) == 0:
        raise ValueError(f"Name '{name}' is not a known axis name. Found nothing")
    return axes[0]


def _next_integer(value: float) -> int:
    ivalue = round(value)
    if abs(ivalue - value) < 0.0001:
        return int(ivalue + 1)
    if ivalue < value:
        return int(ivalue + 1)
    return int(ivalue)


def _previous_integer(value: float) -> int:
    ivalue = round(value)
    if abs(ivalue - value) < 0.0001:
        return int(ivalue - 1)
    if ivalue > value:
        return int(ivalue - 1)
    return int(ivalue)


def _get_interpoled_index(data, pos) -> float | int:
    i = numpy.argmin(numpy.abs(data - pos))
    if i == 0:
        return i
    elif i == len(data) - 1:
        return i
    else:
        ia = i - 1
        ib = i + 1
        # FIXME: There is probably something simpler
        if data[ib] < pos < data[i]:
            i0, i1 = ib, i
        elif data[i] < pos < data[ib]:
            i0, i1 = i, ib
        elif data[ia] < pos < data[i]:
            i0, i1 = ia, i
        else:  # if data[i] < pos < data[ia]:
            i0, i1 = i, ia
    # FIXME: We should use a linarg here
    p0 = data[i0]
    p1 = data[i1]
    coef = (pos - p0) / (p1 - p0)
    return i0 + coef


@custom_error_msg(
    TypeError,
    "intended usage: curs() Hint:",
    display_original_msg=True,
)
@typecheck
def curs():
    """
    Curs command: allow a quick adjust the position of a motor from a scan.
    """
    flint = get_flint()
    plot = flint.get_live_plot("default-curve")
    axis_name = plot.xaxis_channel_name
    channel_name = axis_name[5:] if axis_name.startswith("axis:") else axis_name

    try:
        scan = current_session.scans[-1]
    except IndexError:
        raise RuntimeError("Curs: No scan found")

    xdata = scan.streams[channel_name][:]
    index: float | int = 0
    pos = xdata[index]
    move_to = None

    def update_display():
        plot.update_axis_marker("curs", axis_name, position=pos, text="curs")

    update_display()

    def render():
        """
        Build the prompt to display:
        """
        nonlocal index, pos, xdata
        # FIXME: Use the nb digits of the axis
        # FIXME: Use the unit of the axis
        return 1, f"index: 0/{index}/{len(xdata)}  pos: {pos:0.3f}"

    print("")
    print_help(channel_name)

    k_list = ["escape", "enter", "left", "right"]
    k_list.extend(["m", "p", "x", "q", "h"])
    k_list.extend(["M", "P", "X", "Q", "H"])

    # Treat received events.
    tips = "[Q]uit  [H]elp"
    with text_block(render, key_bindings=k_list, extra_status_bar=tips) as tblock:
        while True:
            key = tblock.wait_key_pressed().lower()

            if key in ["h", "?"]:
                print_help()
            elif key in ["x", "q", "escape", "c-c", "enter"]:
                print("exit / no move")
                break

            elif key == "m":
                print(f"Move axis {channel_name} to {pos}")
                move_to = pos
                break

            elif key == "p":
                displayed_channels = plot.displayed_channels
                if len(displayed_channels) == 0:
                    print("No counter to fit")
                else:
                    counter = get_counter(plot.displayed_channels[0])
                    pos = peak(scan=scan, axis=channel_name, counter=counter)
                    index = _get_interpoled_index(xdata, pos)
                    update_display()

            elif key == "left":
                index = _previous_integer(index)
                if index < 0:
                    index = 0
                pos = xdata[index]
                update_display()

            elif key == "right":
                index = _next_integer(index)
                if index >= len(xdata):
                    index = len(xdata) - 1
                pos = xdata[index]
                update_display()

            else:
                print("Unhandled key: {key}")

    if move_to is not None:
        if axis_name.startswith("axis:"):
            axis = _get_axis_by_name(axis_name[5:])
            umv(axis, move_to)
        else:
            print(f"Object '{axis_name}' can't be moved")
