# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.


"""
SpeedgoatUtils class: Collection of useful functions.
"""

from __future__ import annotations

import typing
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import gevent
from matplotlib.mlab import psd, csd, cohere
from scipy.io import savemat
from scipy.signal import dfreqresp

if typing.TYPE_CHECKING:
    from .speedgoat_counter import SpeedgoatHdwCounter


class SpeedgoatUtils:
    """
    Collection of useful functions
    used in speedgoat_hardware.py
    """

    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._acq = self._speedgoat.acq

    @staticmethod
    def display_counters(counters: list[SpeedgoatHdwCounter], update_time: float = 0.1):
        """
        Display counters live until user interruption (ctrl-c).

        Arguments:
            counters: A list of hardware counters
            update_time: Interval between read and redisplay
        """
        from bliss.shell.standard import text_block

        values: dict[SpeedgoatHdwCounter, typing.Any] = {}

        # Estimate column width
        name_w = max(len("Counter"), *(len(c.name) for c in counters))
        value_w = max(len("Value"), *(len(c._formated_value) for c in counters))
        unit_w = max(len("Unit"), *(len(c.unit or "") for c in counters))

        def render():
            block = f"| {'Counter':^{name_w}} | {'Value':^{value_w}} | {'Unit':^{unit_w}} |\n"
            block += f"|-{'-' * name_w}-+-{'-' * value_w}-+-{'-' * unit_w}-|\n"
            for counter in counters:
                unit = counter.unit or ""
                block += f"| {counter.name:<{name_w}} | {counter._formated_value:>{value_w}} | {unit:^{unit_w}} |\n"

            return len(counters) + 2, block

        with text_block(render=render):
            while True:
                for c in counters:
                    values[c] = c.value
                gevent.sleep(update_time)

    def time_display(
        self, counters, duration=10, decimation=1, directory=None, file_name=None
    ):
        """Record and display Speedgoat counters."""

        # Configure Acquisition
        self._acq.prepare_time(duration, counters, decimation=decimation)

        # Start the Acquisition
        self._acq.start(silent=False, wait=True)

        # Get Acquisition Data
        data = self._acq.get_data()
        t = (
            self._speedgoat._Ts
            * decimation
            * np.arange(0, np.size(data[counters[0].name]), 1)
        )

        # Plot the identified transfer function
        fig = plt.figure(dpi=150)
        ax = fig.add_subplot(1, 1, 1)

        for counter in counters:
            ax.plot(
                t, data[counter.name], "-", label=f"{counter.name} [{counter.unit}]"
            )

        ax.set_xscale("linear")
        ax.set_yscale("linear")
        ax.grid(True, which="both", axis="both")
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Amplitude")
        ax.legend()

        if directory is not None and file_name is not None:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            savemat(f"{directory}/{now}_{file_name}.mat", data)

            fig.savefig(f"{directory}/{now}_{file_name}.pdf")
            fig.savefig(f"{directory}/{now}_{file_name}.png")

        plt.close(fig)

        return data, t

    def spectral_analysis(
        self,
        counters,
        duration=10,
        time_averaging=1,
        decimation=1,
        directory=None,
        file_name=None,
        xlim_min=None,
        xlim_max=None,
        ylim_min=None,
        ylim_max=None,
    ):
        """
        Compute the Power Spectral Density of Speedgoat counters.
        """

        assert (
            duration > time_averaging
        ), "duration should be larger than time_averaging"

        # Configure Acquisition
        self._acq.prepare_time(duration, counters, decimation=decimation)

        # Start the Acquisition
        self._acq.start(silent=False, wait=True)

        # Get Acquisition Data
        data = self._acq.get_data()

        # Plot the identified transfer function
        win = np.hanning(int(time_averaging / (decimation * self._speedgoat._Ts)))
        fig = plt.figure(dpi=150)
        ax = fig.add_subplot(1, 1, 1)

        psd_data = {}

        for counter in counters:
            [Pxx, f] = psd(
                data[counter.name],
                window=win,
                NFFT=len(win),
                Fs=int(1 / (decimation * self._speedgoat._Ts)),
                noverlap=int(len(win) / 2),
                detrend="mean",
            )
            psd_data[counter.name] = Pxx
            psd_data["f"] = f
            ax.plot(
                f,
                np.sqrt(np.abs(Pxx)),
                "-",
                label=f"{counter.name}: {np.std(data[counter.name]):.2e} {counter.unit}rms",
            )

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.grid(True, which="both", axis="both")
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("Amplitude Spectral Density [unit/sqrt(Hz)]")

        if xlim_min is not None:
            ax.set_xlim(left=xlim_min)
        else:
            ax.set_xlim(left=1 / time_averaging)

        if xlim_max is not None:
            ax.set_xlim(right=xlim_max)
        else:
            ax.set_xlim(right=0.5 / (decimation * self._speedgoat._Ts))

        if ylim_min is not None:
            ax.set_ylim(bottom=ylim_min)
        if ylim_max is not None:
            ax.set_ylim(top=ylim_max)

        ax.legend()

        if directory is not None and file_name is not None:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            savemat(f"{directory}/{now}_{file_name}.mat", data)
            fig.savefig(f"{directory}/{now}_{file_name}.pdf")
            fig.savefig(f"{directory}/{now}_{file_name}.png")

        plt.close(fig)

        return psd_data

    def identify_plant(
        self,
        generator,
        counter_in,
        counters_out,
        directory=None,
        file_name=None,
        time_averaging=None,
        plot_coherence=True,
        xlim_min=None,
        xlim_max=None,
        ylim_min=None,
        ylim_max=None,
    ):
        """Computes the transfer function from between counter_in and counters_out using given generator.
        Save Data and figure in the specified directory with given filename.
        The duration of the identification is equal to the duration of the generator."""

        # Configure Acquisition - Start the acquisition exactly when the generator starts
        self._acq.prepare_time(
            generator.duration,
            [counter_in] + counters_out,
            start_path=f"{self._speedgoat._program.name}/{generator._unique_name}/detect_trig_start/FixPt Relational Operator",
        )

        # Start the Acquisition (waiting for generator to start...)
        self._acq.start(silent=True, wait=False)

        # Start the Generator
        generator.start()

        # Get Acquisition Data
        data = self._acq.get_data()

        # Plot the identified transfer function
        if time_averaging is None:
            time_averaging = generator.duration / 10

        win = np.hanning(int(time_averaging * self._speedgoat._Fs))
        fig, axs = plt.subplots(2, 1, dpi=150, sharex=True)

        for counter_out in counters_out:
            self._tfestimate(
                data[counter_in.name],
                data[counter_out.name],
                win=win,
                Fs=int(self._speedgoat._Fs),
                plot=True,
                axs=axs,
                legend=f"{counter_in.name} to {counter_out.name}",
            )

        if xlim_min is not None:
            axs[0].set_xlim(left=xlim_min)
        else:
            axs[0].set_xlim(left=1 / time_averaging)

        if xlim_max is not None:
            axs[0].set_xlim(right=xlim_max)
        else:
            axs[0].set_xlim(right=0.5 / self._speedgoat._Ts)

        if ylim_min is not None:
            axs[0].set_ylim(bottom=ylim_min)
        if ylim_max is not None:
            axs[0].set_ylim(top=ylim_max)

        axs[0].legend()
        axs[1].set_ylim(-180, 180)

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if directory is not None and file_name is not None:
            savemat(f"{directory}/{now}_{file_name}.mat", data)
            fig.savefig(f"{directory}/{now}_{file_name}.pdf")
            fig.savefig(f"{directory}/{now}_{file_name}.png")

            plt.close(fig)

        if plot_coherence:
            # Plot the Coherence
            fig = plt.figure(dpi=150)
            ax = fig.add_subplot(1, 1, 1)

            for counter_out in counters_out:
                self._mscohere(
                    data[counter_in.name],
                    data[counter_out.name],
                    win=win,
                    Fs=int(self._speedgoat._Fs),
                    plot=True,
                    ax=ax,
                    legend=f"{counter_in.name} to {counter_out.name}",
                )

            if xlim_min is not None:
                ax.set_xlim(left=xlim_min)
            else:
                ax.set_xlim(left=1 / time_averaging)

            if xlim_max is not None:
                ax.set_xlim(right=xlim_max)
            else:
                ax.set_xlim(right=0.5 / self._speedgoat._Ts)

            ax.legend()

            if directory is not None and file_name is not None:
                fig.savefig(f"{directory}/{now}_{file_name}_cohere.pdf")
                fig.savefig(f"{directory}/{now}_{file_name}_cohere.png")

            plt.close(fig)

    def _tfestimate(
        self, x, y, win, Fs, plot=False, axs=None, legend="", color=None, alpha=None
    ):
        """Computes the transfer function from x to y.
        win is a windowing function.
        Fs is the sampling frequency in [Hz]"""
        nfft = len(win)

        [Pyx, f] = csd(
            x,
            y,
            window=win,
            NFFT=nfft,
            Fs=int(Fs),
            noverlap=int(nfft / 2),
            detrend="mean",
        )
        Pxx = psd(
            x, window=win, NFFT=nfft, Fs=int(Fs), noverlap=int(nfft / 2), detrend="mean"
        )[0]

        G = Pyx / Pxx

        if plot:
            if axs is None:
                axs = plt.subplots(2, 1, dpi=150, sharex=True)[1]
            axs[0].plot(f, np.abs(G), "-", label=legend)
            axs[0].set_yscale("log")
            axs[0].grid(True, which="both", axis="both")
            axs[0].set_ylabel("Amplitude")

            axs[1].plot(f, 180 / np.pi * np.angle(G), "-")
            axs[1].set_xscale("log")
            axs[1].set_ylim(-180, 180)
            axs[1].grid(True, which="both", axis="both")
            axs[1].set_yticks(np.arange(-180, 180.1, 45))
            axs[1].set_xlabel("Frequency [Hz]")
            axs[1].set_ylabel("Phase [deg]")
            if color is not None:
                axs[0].set_color(color)

            if alpha is not None:
                axs[0].set_alpha(alpha)

        return G, f

    def _mscohere(self, x, y, win, Fs, plot=False, ax=None, legend=""):
        """Computes the coherence from x to y.
        win is a windowing function.
        Fs is the sampling frequency in [Hz]"""
        nfft = len(win)

        [coh, f] = cohere(
            x,
            y,
            window=win,
            NFFT=nfft,
            Fs=int(Fs),
            noverlap=int(nfft / 2),
            detrend="mean",
        )

        if plot:
            if ax is None:
                fig = plt.figure(dpi=150)
                ax = fig.add_subplot(1, 1, 1)
            ax.plot(f, np.abs(coh), "-", label=legend)
            ax.set_yscale("linear")
            ax.set_xscale("log")
            ax.grid(True, which="both", axis="both")
            ax.set_ylim(0, 1)
            ax.set_xlabel("Frequency [Hz]")
            ax.set_ylabel("Coherence")

        return coh, f

    def _pwelch(self, x, win, Fs, ax=None, plot=False, label=""):
        nfft = len(win)
        [Pxx, f] = psd(
            x, window=win, NFFT=nfft, Fs=int(Fs), noverlap=int(nfft / 2), detrend="mean"
        )

        if plot:
            if ax is not None:
                ax.plot(f, np.sqrt(np.abs(Pxx)), "-", label=label)
            else:
                plt.plot(f, np.sqrt(np.abs(Pxx)), "-", label=label)
                plt.yscale("log")
                plt.grid(True, which="both", axis="both")
                plt.xlabel("Frequency [Hz]")
                plt.ylabel("Amplitude Spectral Density")

        return Pxx, f

    def _bode_plot(
        self,
        Gs,
        f_exp=None,
        G_exp=None,
        combine=False,
        label_exp="Experimental",
        directory=None,
        file_name=None,
    ):
        """
        Plot Bode plots of discrete transfer functions and optionally experimental data.

        Parameters
        ----------
        Gs : TransferFunctionDiscrete or list of them
        f_exp : array-like, optional
            Experimental frequency points (Hz)
        G_exp : array-like, optional
            Experimental transfer function values (complex)
        combine : bool
            If True, multiply all Gs together (and optionally with experimental G_exp)
        """
        # Make sure Gs is a list
        if not isinstance(Gs, (list, tuple)):
            Gs = [Gs]

        # Check dt consistency
        dts = [G.dt for G in Gs]
        if not all(dt == dts[0] for dt in dts):
            raise ValueError(
                "All transfer functions must have the same sampling time dt"
            )
        dt = dts[0]

        # Frequency vector in [Hz]
        if f_exp is None:
            f_exp = np.logspace(np.log10(1e-3 / dt / 2), np.log10(1 / dt / 2), 1000)
        else:
            if f_exp[0] == 0:
                f_exp = np.delete(f_exp, 0)
                G_exp = np.delete(G_exp, 0)

        # Compute frequency response of each model at given frequencies
        H_list = []
        for G in Gs:
            _, H = dfreqresp(
                G, w=f_exp * np.pi * dt * 2
            )  # Convert from [Hz] to [rad/sample] (goes up to pi rad / sample)
            H_list.append(H)

        # Combine if requested
        if combine:
            H_combined = np.ones_like(H_list[0])
            for H in H_list:
                H_combined *= H
            if G_exp is not None:
                H_combined *= G_exp
            H_list = [H_combined]

        # Plotting
        fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        # Plot each model
        for i, H in enumerate(H_list):
            label = f"Model {i + 1}" if len(H_list) > 1 else "Combined"
            ax_mag.semilogx(f_exp[0:-2], np.abs(H[0:-2]), label=label)
            ax_phase.semilogx(f_exp[0:-2], np.angle(H[0:-2], deg=True))

        # Plot experimental data if not combined
        if G_exp is not None and not combine:
            ax_mag.semilogx(f_exp[0:-2], np.abs(G_exp[0:-2]), label=label_exp)
            ax_phase.semilogx(
                f_exp[0:-2], np.angle(G_exp[0:-2], deg=True), markersize=4
            )

        # Labels
        ax_mag.set_yscale("log")
        ax_mag.set_ylabel("Magnitude")
        ax_phase.set_ylabel("Phase [deg]")
        ax_phase.set_xlabel("Frequency [Hz]")
        ax_mag.grid(True, which="both")
        ax_phase.grid(True, which="both")
        ax_phase.set_ylim(-180, 180)
        ax_phase.set_yticks(np.arange(-180, 180.1, 45))
        ax_mag.legend()
        ax_mag.set_xlim([f_exp[0], f_exp[-1]])
        plt.tight_layout()

        if directory is not None and file_name is not None:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            fig.savefig(f"{directory}/{now}_{file_name}_cohere.pdf")
            fig.savefig(f"{directory}/{now}_{file_name}_cohere.png")
            plt.close(fig)

        else:
            plt.show()
