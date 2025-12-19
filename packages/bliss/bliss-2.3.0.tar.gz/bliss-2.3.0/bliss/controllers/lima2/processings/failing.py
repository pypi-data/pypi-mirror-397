# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import logging

from bliss.controllers.lima2.counter import FrameCounter
from bliss.controllers.lima2.settings import Settings, setting_property
from bliss.controllers.lima2.tabulate import tabulate

from lima2.client import services

_logger = logging.getLogger("bliss.ctrl.lima2.processing")

ALLOWED_VERSIONS = ("core-1.0.0", "dectris-1.0.0")
"""
Set of versions of the Lima2 C++ Failing pipeline that this Processing class supports.

Before instantiating the Processing object, we should check whether the current version
loaded by the Lima2 backend matches one of these. If not, we possibly have an API
mismatch, and we're likely to run into issues later.
"""


class Processing(Settings):
    """Failing processing user interface"""

    def __init__(self, config, pipeline: services.Pipeline):
        self._device = None
        self._params = pipeline.default_params(processing_name="LimaProcessingFailing")
        super().__init__(config, path=["failing"])

    def _init_with_device(self, device):
        self._device = device
        self._frame_cnt = FrameCounter("frame", device._frame_cc, None)

    @setting_property(default=False)
    def failed_on_prepare(self) -> bool:
        return self._params["failed_on_prepare"]

    @failed_on_prepare.setter
    def failed_on_prepare(self, value: bool) -> None:
        self._params["failed_on_prepare"] = value

    @setting_property(default=False)
    def failed_on_activate(self) -> bool:
        return self._params["failed_on_activate"]

    @failed_on_activate.setter
    def failed_on_activate(self, value: bool) -> None:
        self._params["failed_on_activate"] = value

    @setting_property(default=0)
    def failed_frame_idx(self) -> bool:
        return self._params["failed_frame_idx"]

    @failed_frame_idx.setter
    def failed_frame_idx(self, value: int) -> None:
        self._params["failed_frame_idx"] = value

    def __info__(self):
        def format(title, params):
            return f"{title}:\n" + tabulate(params) + "\n"

        return format("Failing", self._params)

    @property
    def counters(self):
        return [self._frame_cnt]

    @property
    def counter_groups(self):
        return {"default": self.counters}
