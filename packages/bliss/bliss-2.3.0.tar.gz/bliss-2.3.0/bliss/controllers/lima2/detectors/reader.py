# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numbers

from bliss.common.utils import typecheck
from bliss.common.counter import SamplingCounter
from bliss.common.protocols import counter_namespace

from bliss.controllers.lima2.tabulate import tabulate
from bliss.controllers.lima2.controller import DetectorStatusController
from bliss.controllers.lima2.settings import Settings, setting_property

ALLOWED_VERSIONS = ("core-1.0.0",)
"""
Set of versions of the Lima2 C++ Reader plugin that this Detector class supports.

Before instantiating the Detector object, we should check whether the current version
running in the Lima2 backend matches one of these. If not, we possibly have an API
mismatch, and we're likely to run into issues later.
"""


class Detector(Settings):
    """Reader detector user interface"""

    def __init__(self, device):
        """
        {
            "base_path": "/tmp",
            "dataset_path": "/entry_0000/measurement/data",
            "file_type": "nexus",
            "filename_format": "{filename_prefix}_{filename_rank}_{file_number:05d}{filename_suffix}",
            "filename_prefix": "lima2",
            "filename_rank": 0,
            "filename_suffix": ".h5",
            "frame_slice": {"count": 0,
                            "start": 0,
                            "stride": 1},
            "nb_frames_per_file": 50,
            "start_number": 0,
        }

        """
        self._params = device._ctrl_params["det"]
        super().__init__(device._config, path=["reader"])

        self._det_cc = DetectorStatusController(device)
        self._temperature_cnt = SamplingCounter(
            "temperature", self._det_cc, unit="degC"
        )
        self._humidity_cnt = SamplingCounter("humidity", self._det_cc, unit="%")

    @setting_property(default="/tmp")
    def base_path(self):
        return self._params["base_path"]

    @base_path.setter
    @typecheck
    def base_path(self, value: str):
        self._params["base_path"] = value

    @setting_property(default="/entry_0000/measurement/data")
    def dataset_path(self):
        return self._params["dataset_path"]

    @dataset_path.setter
    @typecheck
    def dataset_path(self, value: str):
        self._params["dataset_path"] = value

    @setting_property(default="nexus")
    def file_type(self):
        return self._params["file_type"]

    @file_type.setter
    @typecheck
    def file_type(self, value: str):
        self._params["file_type"] = value

    @setting_property(
        default="{filename_prefix}_{filename_rank}_{file_number:05d}{filename_suffix}"
    )
    def filename_format(self):
        return self._params["filename_format"]

    @filename_format.setter
    @typecheck
    def filename_format(self, value: str):
        self._params["filename_format"] = value

    @setting_property(default="lima2")
    def filename_prefix(self):
        return self._params["filename_prefix"]

    @filename_prefix.setter
    @typecheck
    def filename_prefix(self, value: str):
        self._params["filename_prefix"] = value

    @setting_property(default=0)
    def filename_rank(self):
        return self._params["filename_rank"]

    @filename_rank.setter
    @typecheck
    def filename_rank(self, value: int):
        self._params["filename_rank"] = value

    @setting_property(default=".h5")
    def filename_suffix(self):
        return self._params["filename_suffix"]

    @filename_suffix.setter
    @typecheck
    def filename_suffix(self, value: str):
        self._params["filename_suffix"] = value

    @setting_property(default=0)
    def frame_slice_start(self):
        return self._params["frame_slice"]["start"]

    @frame_slice_start.setter
    @typecheck
    def frame_slice_start(self, value: int):
        self._params["frame_slice"]["start"] = value

    @setting_property(default=0)
    def frame_slice_count(self):
        return self._params["frame_slice"]["count"]

    @frame_slice_count.setter
    @typecheck
    def frame_slice_count(self, value: int):
        self._params["frame_slice"]["count"] = value

    @setting_property(default=1)
    def frame_slice_stride(self):
        return self._params["frame_slice"]["stride"]

    @frame_slice_stride.setter
    @typecheck
    def frame_slice_stride(self, value: int):
        self._params["frame_slice"]["stride"] = value

    @setting_property(default=50)
    def nb_frames_per_file(self):
        return self._params["nb_frames_per_file"]

    @nb_frames_per_file.setter
    @typecheck
    def nb_frames_per_file(self, value: int):
        self._params["nb_frames_per_file"] = value

    @setting_property(default=16)
    def nb_prefetch_frames(self):
        return self._params["nb_prefetch_frames"]

    @nb_prefetch_frames.setter
    @typecheck
    def nb_prefetch_frames(self, value: numbers.Integral):
        self._params["nb_prefetch_frames"] = value

    def __info__(self):
        return tabulate(self._params) + "\n"

    @property
    def counters(self):
        return [
            self._temperature_cnt,
            self._humidity_cnt,
        ]

    @property
    def counter_groups(self):
        res = {}
        res["health"] = counter_namespace([self._temperature_cnt, self._humidity_cnt])
        return res
