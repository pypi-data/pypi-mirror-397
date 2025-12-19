# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
SPEEDGOAT Signal filters
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import dlti, dfreqresp

from bliss.shell.formatters import tabulate
from bliss.shell.formatters.table import IncrementalTable
from bliss.common.utils import RED


class SpeedgoatHdwFilterController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._system = speedgoat._system
        self._program = speedgoat._program
        self._param_tree = self._program.tree.params

        self._filters: dict[str, SpeedgoatHdwFilter] | None = None
        self._load()

    def __info__(self, debug=False):
        if self._filters is None:
            return "\n    No Filter in the model"

        if debug:
            lines = [["Name", "Path", "Type", "Parameters"]]
        else:
            lines = [["Name", "Type", "Parameters"]]
        tab = IncrementalTable(lines, col_sep=" | ", flag="", lmargin="  ", align="<")
        for _filter in self._filters.values():
            if debug:
                tab.add_line(
                    [
                        _filter._name,
                        _filter._unique_name,
                        _filter._type,
                        ", ".join(parameter for parameter in _filter._filter_params),
                    ]
                )
            else:
                tab.add_line(
                    [
                        _filter._name,
                        _filter._type,
                        ", ".join(parameter for parameter in _filter._filter_params),
                    ]
                )
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    def _load(self):
        """Automatically discover all filters present in the model."""
        filters = self._speedgoat._get_all_objects_from_key("bliss_filter")
        if len(filters) > 0:
            self._filters = {}
            for _filter in filters:
                filter_type = self._speedgoat.parameter.get(
                    f"{_filter}/filter_type/String"
                )

                # Initialize all filters depending on their type
                if filter_type == "first_order_lpf":
                    sp_filter = SpeedgoatFirstOrderLowPassFilter(
                        self._speedgoat, _filter
                    )
                elif filter_type == "first_order_hpf":
                    sp_filter = SpeedgoatFirstOrderHighPassFilter(
                        self._speedgoat, _filter
                    )
                elif filter_type == "second_order_lpf":
                    sp_filter = SpeedgoatSecondOrderLowPassFilter(
                        self._speedgoat, _filter
                    )
                elif filter_type == "second_order_hpf":
                    sp_filter = SpeedgoatSecondOrderHighPassFilter(
                        self._speedgoat, _filter
                    )
                elif filter_type == "integrator":
                    sp_filter = SpeedgoatIntegratorFilter(self._speedgoat, _filter)
                elif filter_type == "notch":
                    sp_filter = SpeedgoatNotchFilter(self._speedgoat, _filter)
                elif filter_type == "lead":
                    sp_filter = SpeedgoatLeadFilter(self._speedgoat, _filter)
                elif filter_type == "lag":
                    sp_filter = SpeedgoatLagFilter(self._speedgoat, _filter)
                elif filter_type == "remove_dc":
                    sp_filter = SpeedgoatRemoveDcFilter(self._speedgoat, _filter)
                elif filter_type == "moving_average":
                    sp_filter = SpeedgoatMovingAverageFilter(self._speedgoat, _filter)
                elif filter_type == "general_fir":
                    sp_filter = SpeedgoatGeneralFirFilter(self._speedgoat, _filter)
                elif filter_type == "general_iir":
                    sp_filter = SpeedgoatGeneralIirFilter(self._speedgoat, _filter)
                else:
                    sp_filter = SpeedgoatHdwFilter(self._speedgoat, _filter)

                if hasattr(self, sp_filter._name):
                    print(
                        f"{RED('WARNING')}: Filter '{sp_filter._name}' already exists"
                    )
                    return
                else:
                    setattr(self, sp_filter._name, sp_filter)
                    self._filters[sp_filter._name] = sp_filter


class SpeedgoatHdwFilter:
    def __init__(self, speedgoat, unique_name):
        self._speedgoat = speedgoat
        self._unique_name = unique_name
        self._type = None
        self._filter_params = []

    def __info__(self):
        return tabulate.tabulate(
            self._get_info_lines(), tablefmt="plain", stralign="right"
        )

    def _get_info_lines(self):
        lines = []
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
        lines.append(["", ""])
        lines.append(["Type", self.type])
        return lines

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
        return self._speedgoat.parameter.get(f"{self._unique_name}/bliss_filter/String")

    def enable(self):
        self._speedgoat.parameter.set(f"{self._unique_name}/enable/Value", 1)

    def disable(self):
        self._speedgoat.parameter.set(f"{self._unique_name}/enable/Value", 0)

    @property
    def type(self):
        return self._speedgoat.parameter.get(f"{self._unique_name}/filter_type/String")

    @property
    def enabled(self):
        return bool(self._speedgoat.parameter.get(f"{self._unique_name}/enable/Value"))

    @property
    def input(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/input")

    @property
    def output(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/output")

    def _plot_transfer_function(self):
        G = self._get_transfer_function()
        Fs = self._speedgoat._Fs

        w, h = dfreqresp(G)
        w = w / 2 / np.pi * Fs

        fig, axs = plt.subplots(2, 1, dpi=150, sharex=True)
        axs[0].plot(w, np.abs(h), "-")
        axs[0].set_yscale("log")
        axs[0].grid(True, which="both", axis="both")
        axs[0].set_ylabel("Amplitude")

        axs[1].plot(w, 180 / np.pi * np.angle(h), "-")
        axs[1].set_xscale("log")
        axs[1].set_ylim(-180, 180)
        axs[1].grid(True, which="both", axis="both")
        axs[1].set_yticks(np.arange(-180, 180.1, 45))
        axs[1].set_xlabel("Frequency [Hz]")
        axs[1].set_ylabel("Phase [deg]")
        axs[0].set_xlim([1, Fs / 2])
        plt.tight_layout()
        plt.show()


class SpeedgoatFirstOrderLowPassFilter(SpeedgoatHdwFilter):
    """First Order Low Pass Filter, only parameter is the cut-off frequency."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["wn"]
        self._type = "First Order Low Pass"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        for param in self._filter_params:
            lines.append([param, getattr(self, param)])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def wn(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_wn")

    @wn.setter
    def wn(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/wn", value)
        except Exception:
            print("wn is dynamically set within the Speedgoat")

    def _get_transfer_function(self):
        dt = self._speedgoat._ts
        wn = self.wn

        num = np.array([dt * wn, dt * wn])
        den = np.array([dt * wn + 2, dt * wn - 2])

        return dlti(num, den, dt=dt)


class SpeedgoatFirstOrderHighPassFilter(SpeedgoatHdwFilter):
    """First Order High Pass Filter, only parameter is the cut-off frequency."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["wn"]
        self._type = "First Order High Pass"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        for param in self._filter_params:
            lines.append([param, getattr(self, param)])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def wn(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_wn")

    @wn.setter
    def wn(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/wn", value)
        except Exception:
            print("wn is dynamically set within the Speedgoat")

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts
        wn = self.wn

        num = np.array([2, -2])
        den = np.array([dt * wn + 2, dt * wn - 2])

        return dlti(num, den, dt=dt)


class SpeedgoatSecondOrderLowPassFilter(SpeedgoatHdwFilter):
    """Second Order Low Pass Filter, parameters are the cut-off frequency and the damping ratio."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["wn", "xi"]
        self._type = "Second Order Low Pass"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        for param in self._filter_params:
            lines.append([param, getattr(self, param)])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def xi(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_xi")

    @xi.setter
    def xi(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/xi", value)
        except Exception:
            print("xi is dynamically set within the Speedgoat")

    @property
    def wn(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_wn")

    @wn.setter
    def wn(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/wn", value)
        except Exception:
            print("wn is dynamically set within the Speedgoat")

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts
        wn = self.wn
        xi = self.xi

        num = np.array(
            [(dt**2) * (wn**2), 2 * (dt**2) * (wn**2), (dt**2) * (wn**2)]
        )
        den = np.array(
            [
                (dt**2) * (wn**2) + 4 * xi * dt * wn + 4,
                2 * (dt**2) * (wn**2) - 8,
                (dt**2) * (wn**2) - 4 * dt * wn * xi + 4,
            ]
        )

        return dlti(num, den, dt=dt)


class SpeedgoatSecondOrderHighPassFilter(SpeedgoatHdwFilter):
    """Second Order High Pass Filter, parameters are the cut-off frequency and the damping ratio."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["wn", "xi"]
        self._type = "Second Order High Pass"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        for param in self._filter_params:
            lines.append([param, getattr(self, param)])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def xi(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_xi")

    @xi.setter
    def xi(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/xi", value)
        except Exception:
            print("xi is dynamically set within the Speedgoat")

    @property
    def wn(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_wn")

    @wn.setter
    def wn(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/wn", value)
        except Exception:
            print("wn is dynamically set within the Speedgoat")

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts
        wn = self.wn
        xi = self.xi

        num = np.array([4, -8, 4])
        den = np.array(
            [
                (dt**2) * (wn**2) + 4 * xi * dt * wn + 4,
                2 * (dt**2) * (wn**2) - 8,
                (dt**2) * (wn**2) - 4 * dt * wn * xi + 4,
            ]
        )

        return dlti(num, den, dt=dt)


class SpeedgoatIntegratorFilter(SpeedgoatHdwFilter):
    """Integrator, no parameter."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = []
        self._type = "Integrator"

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts

        num = np.array([dt, dt])
        den = np.array([2, -2])

        return dlti(num, den, dt=dt)


class SpeedgoatNotchFilter(SpeedgoatHdwFilter):
    """Notch Filter, parameters are the frequency of the notch, the gain of the notch
    (that may be <1 or >1) and the damping ratio."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["wn", "xi", "gc"]
        self._type = "Notch"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        for param in self._filter_params:
            lines.append([param, getattr(self, param)])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def xi(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_xi")

    @xi.setter
    def xi(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/xi", value)
        except Exception:
            print("xi is dynamically set within the Speedgoat")

    @property
    def gc(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_gc")

    @gc.setter
    def gc(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/gc", value)
        except Exception:
            print("gc is dynamically set within the Speedgoat")

    @property
    def wn(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_wn")

    @wn.setter
    def wn(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/wn", value)
        except Exception:
            print("wn is dynamically set within the Speedgoat")

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts

        wn = self.wn
        gc = self.gc
        xi = self.xi

        num = np.array(
            [
                dt**2 * wn**2 + 4 * gc * xi * dt * wn + 4,
                2 * dt**2 * wn**2 - 8,
                dt**2 * wn**2 - 4 * gc * xi * dt * wn + 4,
            ]
        )
        den = np.array(
            [
                dt**2 * wn**2 + 4 * xi * dt * wn + 4,
                2 * dt**2 * wn**2 - 8,
                dt**2 * wn**2 - 4 * xi * dt * wn + 4,
            ]
        )

        return dlti(num, den, dt=dt)


class SpeedgoatLeadFilter(SpeedgoatHdwFilter):
    """Lead Filter"""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["wn", "a"]
        self._type = "Lead"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        for param in self._filter_params:
            lines.append([param, getattr(self, param)])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def a(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_a")

    @a.setter
    def a(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/a", value)
        except Exception:
            print("a is dynamically set within the Speedgoat")

    @property
    def wn(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_wn")

    @wn.setter
    def wn(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/wn", value)
        except Exception:
            print("wn is dynamically set within the Speedgoat")

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts

        wn = self.wn
        a = self.a

        num = np.array([2 * a + dt * wn, dt * wn - 2 * a])
        den = np.array([dt * a * wn + 2, dt * a * wn - 2])

        return dlti(num, den, dt=dt)


class SpeedgoatLagFilter(SpeedgoatHdwFilter):
    """lag Filter"""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["wn", "a"]
        self._type = "lag"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        for param in self._filter_params:
            lines.append([param, getattr(self, param)])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def a(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_a")

    @a.setter
    def a(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/a", value)
        except Exception:
            print("a is dynamically set within the Speedgoat")

    @property
    def wn(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_wn")

    @wn.setter
    def wn(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/wn", value)
        except Exception:
            print("wn is dynamically set within the Speedgoat")

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts

        wn = self.wn
        a = self.a

        num = np.array([2 * a**0.5 + dt * a * wn, dt * a * wn - 2 * a**0.5])
        den = np.array([dt * wn + 2 * a**0.5, dt * wn - 2 * a**0.5])

        return dlti(num, den, dt=dt)


class SpeedgoatRemoveDcFilter(SpeedgoatHdwFilter):
    """Filter that can be triggered to remove the DC part of the signal."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._type = "Remove DC"

    @property
    def offset(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_offset")

    @offset.setter
    def offset(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/offset", value)
        except Exception:
            print("offset is dynamically set within the Speedgoat")

    def trigger(self):
        trigger_value = int(
            self._speedgoat.parameter.get(f"{self._unique_name}/start_trigger/Bias")
        )
        self._speedgoat.parameter.set(
            f"{self._unique_name}/start_trigger/Bias", trigger_value + 1
        )

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts

        return dlti([1], [1], dt=dt)


class SpeedgoatMovingAverageFilter(SpeedgoatHdwFilter):
    """Moving average filter (implemented as a FIR filter).
    Only the average time can be tuned."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["avg_time"]
        self._type = "Moving Average"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        for param in self._filter_params:
            lines.append([param, getattr(self, param)])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def max_avg_time(self):
        return (
            self._speedgoat.signal.get(f"{self._unique_name}/param_nb_taps")
            * self._speedgoat._Ts
        )

    @property
    def avg_time(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_avg_time")

    @avg_time.setter
    def avg_time(self, value):
        max_avg_time = self.max_avg_time
        if value > max_avg_time:
            print("avg_time is above the maximum of {max_avg_time:.3f} s")
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/avg_time", value)
        except Exception:
            print("avg_time is dynamically set within the Speedgoat")


class SpeedgoatGeneralFirFilter(SpeedgoatHdwFilter):
    """Finite Impulse Response (FIR) filter.
    Defined by num_coef."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["order", "num_coef"]
        self._type = "General FIR"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        lines.append(["Order", self.order])
        lines.append(
            ["Numerator", "[" + ", ".join(f"{x:.2g}" for x in self.num_coef) + "]"]
        )
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def order(self):
        return len(self.num_coef) - 1

    @property
    def num_coef(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_num_coef")

    @num_coef.setter
    def num_coef(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/num_coef", value)
        except Exception:
            print("num_coef is dynamically set within the Speedgoat")

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts

        return dlti(self.num_coef, [1], dt=dt)


class SpeedgoatGeneralIirFilter(SpeedgoatHdwFilter):
    """Infinite Impulse Response (IIR) filter.
    Defined by num_coef and den_coef."""

    def __init__(self, speedgoat, unique_name):
        super().__init__(speedgoat, unique_name)
        self._filter_params = ["order", "num_coef", "den_coef"]
        self._type = "General IIR"

    def __info__(self):
        lines = super()._get_info_lines()
        lines.append(["", ""])
        lines.append(["Parameters:", ""])
        lines.append(["Order", self.order])
        lines.append(
            ["Numerator", "[" + ", ".join(f"{x:.2g}" for x in self.num_coef) + "]"]
        )
        lines.append(
            ["Denominator", "[" + ", ".join(f"{x:.2g}" for x in self.den_coef) + "]"]
        )
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def order(self):
        return len(self.den_coef) - 1

    @property
    def num_coef(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_num_coef")

    @num_coef.setter
    def num_coef(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/num_coef", value)
        except Exception:
            print("num_coef is dynamically set within the Speedgoat")

    @property
    def den_coef(self):
        return self._speedgoat.signal.get(f"{self._unique_name}/param_den_coef")

    @den_coef.setter
    def den_coef(self, value):
        try:
            self._speedgoat.parameter.set(f"{self._unique_name}/den_coef", value)
        except Exception:
            print("den_coef is dynamically set within the Speedgoat")

    def reset(self):
        reset_states = int(
            self._speedgoat.parameter.get(f"{self._unique_name}/reset/Bias")
        )
        self._speedgoat.parameter.set(
            f"{self._unique_name}/reset/Bias", reset_states + 1
        )

    def _get_transfer_function(self):
        dt = self._speedgoat._Ts

        return dlti(self.num_coef, self.den_coef, dt=dt)
