# -*- coding: utf-8 -*-
#
# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import gevent
import random
import string
import numpy as np

from bliss.shell.standard import print_html

from bliss.common.user_status_info import status_message
from bliss.shell.formatters.table import IncrementalTable

from resyst.client.acq import Acq, AcqState


class SpeedgoatHdwAcquisition:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._system = speedgoat._system
        self._program = speedgoat._program

        self._acq: Acq | None = None

    def __info__(self, debug=False):
        if len(self._program.acqs) == 0:
            return "\n    No Loaded acquisition"

        lines = [["Name", "State", "Decimation", "Nbp", "Signals"]]
        tab = IncrementalTable(lines, col_sep=" | ", flag="", lmargin="  ", align="<")
        for acq in self._program.acqs:
            tab.add_line(
                [
                    acq.name,
                    acq.status.state.name,
                    acq.decimation,
                    f"{acq.nbp:d}",
                    acq.signal_paths[0][len(self._program.name) + 1 :],
                ]
            )
            for i in range(1, len(acq.signal_paths)):
                tab.add_line(
                    ["", "", "", "", acq.signal_paths[i][len(self._program.name) + 1 :]]
                )
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    def prepare(
        self,
        nsample,
        counter_list,
        decimation=1,
        name=None,
        filter_path="",
        start_path="",
        start_pre_samples=0,
    ):
        return self._create_acq(
            counter_list,
            nsample,
            decimation=decimation,
            name=name,
            filter_path=filter_path,
            start_path=start_path,
            start_pre_samples=start_pre_samples,
        )

    def prepare_time(
        self,
        time,
        counter_list,
        decimation=1,
        name=None,
        filter_path="",
        start_path="",
        start_pre_samples=0,
    ):
        nbp = int(time / self._speedgoat._Ts / decimation)
        return self._create_acq(
            counter_list,
            nbp,
            decimation=decimation,
            name=name,
            filter_path=filter_path,
            start_path=start_path,
            start_pre_samples=start_pre_samples,
        )

    def start(self, wait=False, silent=True, name=None):
        """Use to start the acquisition (the Speedgoat will start sending data)"""
        self._program.start_acqs([self._get_acq_from_name(name)])

        if wait:
            self._wait_finished(silent=silent)

    def stop(self, name=None):
        acq = self._get_acq_from_name(name)
        if acq is not None:
            acq.stop()

    def get_data(self, name=None, display=False, debug=False):
        """
        Used to get all data of an acquistion.
        It will wait for the acquisition to be finished (i.e. all data are received by the Resyst server).
        The acquisition is then removed from the server.
        """
        acq = self._get_acq_from_name(name)
        result = {
            self._speedgoat.counter._get_counter_from_full_path(signal_path).name: []
            for signal_path in acq.signal_paths
        }
        timestamp = []

        # Will display the number of points
        with status_message() as update:
            while (self._is_running(name)) or (acq.nb_sample_to_read > 0):
                if acq.nb_sample_to_read > 0:
                    n_to_read = acq.nb_sample_to_read
                    data_acq = acq.get_data(n_to_read)
                    timestamp.append(data_acq["timestamp"])

                    for signal_path in acq.signal_paths:
                        counter_name = (
                            self._speedgoat.counter._get_counter_from_full_path(
                                signal_path
                            ).name
                        )
                        val = data_acq[signal_path]
                        result[counter_name].append(val)

                    if display:
                        update(
                            f"Waiting Speedgoat Acquisition to terminate ({np.sum([t.size for t in timestamp])}/{acq.nbp})"
                        )
                gevent.sleep(0.2)

        # concatenate the bunches for each signal (so result looks like the old get_data)
        for k in list(result.keys()):
            result[k] = np.concatenate(result[k], axis=0)

        if debug:
            if self._is_finished(name):
                print_html(
                    "<success>Acquisition correctly acquired all the points.</success>"
                )
            else:
                print_html(
                    "<warning>Acquisition was not finished (not all points could be acquired by the Resyst server).</warning>"
                )

            # Check if no point is missing by looking at the Timestamp
            timestamp = np.concatenate(timestamp, axis=0)
            timestamp_nom_value = 1e6 * (
                self._speedgoat._Ts * acq.decimation
            )  # Expected timestamp increase in [us]
            step_diff = np.rint(
                np.diff(timestamp) / timestamp_nom_value
            )  # Should always be equal to one

            # Check if there are some missing points
            if not np.all(step_diff == 1):
                print_html(
                    f"<warning>WARNING: There are {np.sum(step_diff - 1)} missing points (maximum {np.max(step_diff) - 1} consecutive missing points)</warning>"
                )

            # Check if correct number of points
            if (
                len(
                    result[
                        self._speedgoat.counter._get_counter_from_full_path(
                            acq.signal_paths[0]
                        ).name
                    ]
                )
                != acq.nbp
            ):
                print_html(
                    f"<warning>WARNING: Incorect number of points: ({len(result[self._speedgoat.counter._get_counter_from_full_path(acq.signal_paths[0]).name])}/{acq.nbp})</warning>"
                )

        # Delete the acquisition (after all data have been retrieved)
        self._program.remove_acq(acq.name)

        return result

    def get_available_data(self, name=None, max_nbp=None):
        acq = self._get_acq_from_name(name)
        result = {}

        # If max_nbp is specified, get at most this number of points
        # Otherwise, get all the available points
        if max_nbp is not None:
            n_to_read = min(max_nbp, acq.nb_sample_to_read)
        else:
            n_to_read = acq.nb_sample_to_read

        data_acq = acq.get_data(n_to_read)

        for signal_path in acq.signal_paths:
            counter_name = self._speedgoat.counter._get_counter_from_full_path(
                signal_path
            ).name
            val = data_acq[signal_path]
            result[counter_name] = val

        return result

    def _create_acq(
        self,
        counters,
        nbp,
        decimation=1,
        name=None,
        filter_path="",
        start_path="",
        start_pre_samples=0,
    ):
        """
        Register one Acquisition on the Resyst server
        """
        if name is None:
            # Create random name if not specified
            name = "".join(random.choices(string.ascii_uppercase, k=5))

        if filter_path != "" and start_path != "":
            print_html(
                "<warning>WARNING: filter_path and start_path cannot be used at the same time</warning>"
            )
            return

        if filter_path != "":  # Trigerred acquisition
            name = "trig_" + name
            if decimation > 1:
                print_html(
                    "<warning>WARNING: When filter_path is used, decimation should be equal to 1</warning>"
                )
        elif start_path != "":  # Start Condition : Monitoring
            name = "moni_" + name
        else:  # Normal Acquisition
            name = "acq_" + name

        # Force no pre-samples when not using a start trigger
        if start_path == "":
            start_pre_samples = 0

        self._acq = Acq(
            name=name,
            signal_paths=[counter._full_path for counter in counters],
            nbp=nbp,
            decimation=decimation,
            filter_path=filter_path,
            start_path=start_path,
            start_pre_samples=start_pre_samples,
        )

        # Automatically add the acquisition
        self._program.add_acq(self._acq)
        return name

    def _remove_acqs(self, acq_prefix_name=""):
        """
        Delete configured acquisition on the Resyst server.
        If acq_prefix_name is not specified, all the acquisitons are removed.
        """
        for acq in self._speedgoat._program.acqs:
            if acq.name.startswith(acq_prefix_name):
                self._program.remove_acq(acq.name)

    def _remove_finished_acqs(self):
        """
        Used to remove all 'done' acquisitions.
        """
        for acq in self._speedgoat._program.acqs:
            if acq.is_done:
                self._program.remove_acq(acq.name)

    def _get_acq_from_name(self, name=None):
        """
        Utility function to easily get the wanted acquisition (or the last loaded one if name is None)
        """
        if name is None:
            return self._acq  # Get the last loaded Acquisition
        else:
            acq_dict = {acq.name: acq for acq in self._program.acqs}
            return acq_dict[name]

    def _is_running(self, name=None):
        """
        Returns whether the acquisition is currently acquiring data or not.
        """
        acq = self._get_acq_from_name(name)
        return acq.status.state == AcqState.RUNNING

    def _is_stopped(self, name=None):
        acq = self._get_acq_from_name(name)
        return acq.status.state == AcqState.STOP

    def _is_finished(self, name=None):
        """
        This means that the Resyst server has received all the wanted data.
        It is possible that the acquisition is stopped, but because not all data
        has been received, _is_finished is False.
        """
        return self._get_acq_from_name(name).is_done

    def _wait_finished(self, silent=True, name=None):
        """
        Blocking function that only returns when the acquisition is no longer running.
        Could be because it has been manually stopped or because all data has been stored by the server.
        """
        acq = self._get_acq_from_name(name)
        with status_message() as update:
            while self._is_running(name):
                if not silent:
                    update(
                        f" Waiting Speedgoat Acquisition to terminate {acq.nb_sample_to_read} (/{acq.nbp})"
                    )
                gevent.sleep(0.2)
        if not silent:
            print("\n")
