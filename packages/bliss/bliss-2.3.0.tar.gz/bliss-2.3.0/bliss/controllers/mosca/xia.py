# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numpy
import enum
from bliss.common.logtools import log_debug, log_error
from bliss.common.protocols import HasMetadataForScan
from bliss.controllers.mosca.base import McaController, TriggerMode

DetectorMode = enum.Enum("DetectorMode", "MCA MAP")


class FalconX(McaController, HasMetadataForScan):

    MCA_REFRESH_RATE_LIMIT = 0.01

    STATS_MAPPING = {
        # MOSCA    :  NxWriter
        "output": "events",
        "icr": "icr",
        "ocr": "ocr",
        "livetime": "trigger_livetime",
        "deadtime": "deadtime",
        "realtime": "realtime",
        "triggers": "triggers",
        "livetime_events": "energy_livetime",
        "deadtime_correction": "deadtime_correction",
    }

    def __info__(self) -> str:
        """
        Add specific information for XIA controllers.
        """
        txt = super().__info__()
        txt += f" detector mode:     {self.hardware.detector_mode}\n"
        txt += f" refresh rate:      {self.hardware.refresh_rate:.4f} s\n"
        txt += f"\n configuration file: {self.configuration_file}\n"
        return txt

    def scan_metadata(self) -> dict:
        return {
            "@NX_class": "NXcollection",
            "configuration_file": self.configuration_file,
        }

    def _load_settings(self) -> None:
        super()._load_settings()

        # Use last configuration file kept in settings.
        last_config_file = self._settings.get("config_file")
        if last_config_file:
            self.configuration_file = last_config_file
        else:
            self._settings["config_file"] = self.hardware.config

    def _prepare_acquisition(self, acq_params: dict) -> None:

        self.hardware.trigger_mode = acq_params["trigger_mode"]
        self.hardware.number_points = acq_params["npoints"]

        preset_time = acq_params["preset_time"]  # seconds

        if acq_params["trigger_mode"] == TriggerMode.SOFTWARE.name:

            # use given refresh_rate or 100ms by default
            refresh_rate = acq_params.setdefault("refresh_rate", 0.1)  # seconds

            # adjust refresh_rate if preset_time is smaller
            if preset_time <= refresh_rate:
                acq_params["refresh_rate"] = refresh_rate = preset_time

            self.refresh_rate = refresh_rate
            self.hardware.preset_value = preset_time * 1000  # milliseconds

        else:

            refresh_rate = acq_params.get("refresh_rate")  # seconds
            if refresh_rate is None:
                refresh_rate = self.hardware.refresh_rate
            else:
                self.refresh_rate = refresh_rate

            # auto tune number of pixels per buffer
            if preset_time <= 2 * refresh_rate:
                ppb_mini = int(numpy.ceil(2 * refresh_rate / preset_time)) + 1
            else:
                ppb_mini = 1

            ppb_default = max(ppb_mini, int(refresh_rate / preset_time))

            ppb = acq_params.get("map_pixels_per_buffer", ppb_default)

            log_debug(
                self,
                "mppb: %s, mppb_mini: %s, mppb_default: %s, refresh_rate: %s, preset_time: %s",
                ppb,
                ppb_mini,
                ppb_default,
                refresh_rate,
                preset_time,
            )

            self.hardware.map_pixels_per_buffer = ppb

    @property
    def refresh_rate(self) -> float:
        return self.hardware.refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value: float) -> None:
        if self.hardware.detector_mode == DetectorMode.MCA.name:
            if value < self.MCA_REFRESH_RATE_LIMIT:
                raise ValueError(
                    f"refresh rate must be >= {self.MCA_REFRESH_RATE_LIMIT}s in SOFTWARE trigger mode"
                )
        self.hardware.refresh_rate = value

    @property
    def detectors_identifiers(self) -> list[str]:
        """return active detectors identifiers list [str] (['module:channel_in_module', ...])"""
        return self.hardware.channels_module_and_index

    @property
    def detectors_aliases(self) -> list[int]:
        """return active detectors channels aliases list [int]"""
        return self.hardware.channels_alias

    @property
    def configuration_file(self) -> str:
        return self.hardware.config

    @configuration_file.setter
    def configuration_file(self, fname: str) -> None:
        current_config = self.hardware.config
        if fname != current_config:
            try:
                self.hardware.config = fname
            except Exception:
                self.hardware.config = current_config
                log_error(
                    self,
                    "loading configuration file '%s' has failed, check MOSCA server for more info.\nCurrent configuration file is: '%s'",
                    fname,
                    current_config,
                )
                fname = current_config

            self._settings["config_file"] = fname
            self.initialize()

    @property
    def configuration_dir(self) -> str:
        return self.hardware.config_path

    @property
    def available_configurations(self) -> list[str]:
        return list(self.hardware.DevXiaGetConfigList())

    def load_configuration(self, config_name: str | None = None) -> None:
        """
        If <config_name> is not None, load it.
        Otherwise, provide an interactive menu to select a config to load.
        """
        from bliss.shell.getval import getval_idx_list

        if config_name is None:
            _config_list = self.available_configurations
            idx, config_name = getval_idx_list(
                _config_list, "Select configuration number"
            )

        # load config
        print(f"Loading {config_name}...")
        self.configuration_file = config_name
