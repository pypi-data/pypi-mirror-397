# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import logging
import traceback

import gevent
from lima2.client import services

from bliss.common.counter import Counter
from bliss.common.protocols import (
    HasMetadataForDataset,
    HasMetadataForScanExclusive,
)
from bliss.controllers.counter import (
    CounterController,
    IntegratingCounterController,
    SamplingCounterController,
)
from bliss.controllers.lima.roi import ArcRoi, Roi, RoiProfile
from bliss.scanning.acquisition.counter import SamplingCounterAcquisitionSlave
from bliss.scanning.chain import AcquisitionSlave
from bliss.scanning.channel import AcquisitionChannel

_logger = logging.getLogger("bliss.ctrl.lima2")


# Logger decorator
def logger(fn):
    def inner(*args, **kwargs):
        _logger.debug(f"Entering {fn.__name__}")
        to_execute = fn(*args, **kwargs)
        _logger.debug(f"Exiting {fn.__name__}")
        return to_execute

    return inner


class DetectorController(
    CounterController, HasMetadataForScanExclusive, HasMetadataForDataset
):
    """
    Detector controller.
    """

    DEVICE_TYPE = "lima2"

    TIMEOUT = 10.0

    @logger
    def __init__(self, device):
        super().__init__(device.name, register_counters=False)

        self._dev = device

    @property
    def device(self):
        return self._dev

    # implements HasMetadataForDataset
    @logger
    def dataset_metadata(self) -> dict:
        description = f"{self._dev.det_info['plugin']}, {self._dev.det_info['model']}"
        pixel_size = self._dev.det_info["pixel_size"]
        return {
            "name": self.name,
            "description": description,
            "x_pixel_size": pixel_size["x"],
            "y_pixel_size": pixel_size["y"],
        }

    # implements HasMetadataForScanExclusive
    @logger
    def scan_metadata(self) -> dict:
        description = f"{self._dev.det_info['plugin']}, {self._dev.det_info['model']}"
        pixel_size = self._dev.det_info["pixel_size"]
        return {
            "type": "lima2",
            "description": description,
            "x_pixel_size": pixel_size["x"],
            "y_pixel_size": pixel_size["y"],
            "x_pixel_size@units": "m",
            "y_pixel_size@units": "m",
            # "camera_settings": camera_settings,
        }

    # }

    # implements CounterController
    # {
    # Called by scan builder (toolbox) after get_default_chain_parameters
    @logger
    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        """
        Returns an AcquisitionObject instance.

        This function is intended to be used by the `ChainNode`.
        `acq_params`, `ctrl_params` and `parent_acq_params` have to be `dict` (`None` not supported)

        In case a incomplete set of `acq_params` is provided `parent_acq_params` may eventually
        be used to complete `acq_params` before choosing which Acquisition Object needs to be
        instantiated or just to provide all necessary `acq_params` to the Acquisition Object.

        parent_acq_params should be inserted into `acq_params` with low priority to not overwrite
        explicitly provided `acq_params` i.e. by using `setdefault`
        """
        _logger.debug(f"{acq_params} {ctrl_params} {parent_acq_params}")

        # avoid cyclic import
        from bliss.scanning.acquisition.lima2 import Lima2AcquisitionMaster

        return Lima2AcquisitionMaster(
            device=self,
            name=self.name,
            ctrl_params=ctrl_params,
            **acq_params,
        )

    # Called first by scan builder (toolbox) to get default scan params
    @logger
    def get_default_chain_parameters(self, scan_params, acq_params):
        """
        Returns completed acq_params with missing values guessed from scan_params
        in the context of default chain i.e. step-by-step scans.
        """
        # scan_params, parameters from user. Additional properties can be added?
        # acq_params "empty" to be filled for master, or filled by master if slaves
        _logger.debug(f"scan_params: {scan_params} acq_params: {acq_params}")

        npoints = scan_params.get("npoints", 1)
        count_time = scan_params.get("count_time", 1.0)

        # Get default trigger mode
        if "software" in self._dev.det_capabilities["trigger_modes"]:
            default_trigger_mode = "software"
        else:
            default_trigger_mode = "internal"

        # USE PROVIDED TRIGGER MODE ELSE USE DEFAULT VALUE
        trigger_mode = acq_params.get("trigger_mode", default_trigger_mode)

        # npoints = acq_params.get("acq_nb_frames", scan_params.get("npoints", 1))

        prepare_once = trigger_mode in (
            "software",
            "external",
            "gate",
        )

        # start always called once, then trigger called once (internal) or multiple times (software)
        start_once = True

        nb_frames = acq_params.get("nb_frames")
        if nb_frames is None:
            nb_frames = npoints if prepare_once else 1

        expo_time = acq_params.get("expo_time")
        if expo_time is None:
            expo_time = count_time

        # Return required parameters
        params = {}
        params["nb_frames"] = nb_frames
        params["expo_time"] = expo_time
        params["trigger_mode"] = trigger_mode
        # params["acq_mode"] = acq_params.get("acq_mode", "SINGLE")
        # params["wait_frame_id"] = range(npoints)
        params["prepare_once"] = prepare_once
        params["start_once"] = start_once
        params["is_saving"] = False

        _logger.debug(f"default_chain_parameters: {params}")
        return params

    def get_current_parameters(self):
        """Should return an exhaustive dict of parameters that will be send
        to the hardware controller at the beginning of each scan.
        These parametes may be overwritten by scan specific ctrl_params
        """

        from copy import deepcopy

        return deepcopy(
            {
                "ctrl": self._dev._ctrl_params,
                "recvs": self._dev._recvs_params,
                "procs": self._dev._processing._params,
            }
        )

    def apply_parameters(self, ctrl_params):
        # Nothing to do
        ...

    # }


class RoiStatAcquisitionObject(AcquisitionSlave):
    def __init__(
        self,
        rois: list[Roi | ArcRoi],
        controller: "RoiStatController",
        pipeline: services.Pipeline,
        npoints,
        ctrl_params,
    ):
        super().__init__(
            controller,
            npoints=npoints,
            ctrl_params=ctrl_params,
            prepare_once=True,
            start_once=True,
        )
        self.pipeline = pipeline
        """Conductor pipeline services."""
        self.rois = rois
        """List of rois."""
        self.channel_by_roi_stat: dict[(str, str), AcquisitionChannel] = {}
        """
        Custom mapping of channels, populated in add_counter. Allows retrieving
        a channel for a given (roi, stat) tuple.
        """

        self.stop_requested = False
        """Set to True by stop()."""

    def add_counter(self, counter):
        """Called for each roi, for each statistic (avg, std, min, max, sum)."""
        self._do_add_counter(counter=counter)

        try:
            name, stat = counter.name.split("_")
        except ValueError:
            raise ValueError(
                f"Cannot parse roi name {counter.name}. Please remove underscores (_)."
            )

        self.channel_by_roi_stat[(name, stat)] = self.channels[-1]

    def reading(self):
        """Launch tasks to fetch and emit statistics for each roi."""

        def fetch_and_emit(roi_idx: int, roi_name: str):
            """Fetch all roi stats for a given roi and emit into the associated channels."""
            for chunk in self.pipeline.reduced_data(
                name="roi_stats",
                channel_idx=roi_idx,
            ):
                if self.stop_requested:
                    # NOTE: prevents "Writing to a closed sink" error when scan
                    # has been aborted.
                    break
                for stat in ("avg", "std", "min", "max", "sum"):
                    self.channel_by_roi_stat[(roi_name, stat)].emit(chunk[stat])

        def on_error(greenlet):
            _logger.error("".join(traceback.format_exception(greenlet.exception)))

        tasks = []
        for i, roi in enumerate(self.rois):
            task = gevent.spawn(fetch_and_emit, i, roi.name)
            task.link_exception(on_error)
            tasks.append(task)

        gevent.joinall(tasks)

    def prepare(self):
        pass

    def start(self):
        pass

    def stop(self):
        self.stop_requested = True

    def trigger(self):
        pass


class RoiStatController(CounterController):
    def __init__(self, roi_stats, pipeline: services.Pipeline, master_controller):
        super().__init__(
            "roi_statistics",  # Automatically prefixed with master_controller name
            master_controller=master_controller,
            register_counters=False,
        )

        self.pipeline = pipeline
        """Conductor pipeline services."""
        self.roi_stats = roi_stats
        """RoiStatistics instance which holds and updates the list of rois."""

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        # Avoid RuntimeError: {'acq_params': [{'count_time': ['null value not allowed']}]}
        # when creating children in create_children_acq_obj

        if "nb_frames" in parent_acq_params:
            nb_frames = parent_acq_params["nb_frames"]
        else:
            nb_frames = acq_params["npoints"]

        return RoiStatAcquisitionObject(
            rois=self.roi_stats.rois,
            controller=self,
            pipeline=self.pipeline,
            npoints=nb_frames,
            ctrl_params=ctrl_params,
        )

    def get_default_chain_parameters(self, scan_params, acq_params):
        try:
            npoints = acq_params["npoints"]
        except KeyError:
            npoints = scan_params["npoints"]

        params = {"npoints": npoints}

        return params


class RoiProfilesAcquisitionObject(AcquisitionSlave):
    """Acquisition object for roi profiles.

    Identical to RoiStatAcquisitionObject except for the reading loop.
    """

    def __init__(
        self,
        rois: list[RoiProfile],
        controller: "RoiProfilesController",
        pipeline: services.Pipeline,
        npoints,
        ctrl_params,
    ):
        super().__init__(
            controller,
            npoints=npoints,
            ctrl_params=ctrl_params,
            prepare_once=True,
            start_once=True,
        )

        self.pipeline = pipeline
        """Conductor pipeline services."""
        self.rois = rois
        """List of roi profiles."""
        self.channel_by_roi_stat: dict[(str, str), AcquisitionChannel] = {}
        """
        Custom mapping of channels, populated in add_counter. Allows retrieving
        a channel for a given (roi, stat) tuple.
        """

        self.stop_requested = False
        """Set to True by stop()."""

    def add_counter(self, counter):
        """Called for each roi, for each statistic (avg, std, min, max, sum)."""
        self._do_add_counter(counter=counter)

        try:
            name, stat = counter.name.split("_")
        except ValueError:
            raise ValueError(
                f"Cannot parse roi name {counter.name}. Please remove underscores (_)."
            )

        self.channel_by_roi_stat[(name, stat)] = self.channels[-1]

    def reading(self):
        """Launch tasks to fetch and emit statistics for each roi."""

        def fetch_and_emit(roi_idx: int, roi_name: str):
            """Fetch all roi stats for a given roi and emit into the associated channels."""

            for chunk in self.pipeline.reduced_data(
                name="roi_profile",
                channel_idx=roi_idx,
            ):
                if self.stop_requested:
                    # NOTE: prevents "Writing to a closed sink" error when scan
                    # has been aborted.
                    break
                for stat in ("avg", "std", "min", "max", "sum"):
                    self.channel_by_roi_stat[(roi_name, stat)].emit(chunk[stat])

        def on_error(greenlet):
            _logger.error("".join(traceback.format_exception(greenlet.exception)))

        tasks = []
        for i, profile in enumerate(self.rois):
            task = gevent.spawn(fetch_and_emit, i, profile.name)
            task.link_exception(on_error)
            tasks.append(task)

        gevent.joinall(tasks)

    def prepare(self):
        pass

    def start(self):
        pass

    def stop(self):
        self.stop_requested = True

    def trigger(self):
        pass


class RoiProfilesController(IntegratingCounterController):
    def __init__(self, roi_profiles, pipeline: services.Pipeline, master_controller):
        super().__init__(
            "roi_profiles",  # Automatically prefixed with master_controller name
            master_controller=master_controller,
            register_counters=False,
        )

        self.pipeline = pipeline
        """Conductor pipeline services."""
        self.roi_profiles = roi_profiles
        """RoiProfiles instance which holds and updates the list of rois."""

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        # Avoid RuntimeError: {'acq_params': [{'count_time': ['null value not allowed']}]}
        # when creating children in create_children_acq_obj

        if "nb_frames" in parent_acq_params:
            nb_frames = parent_acq_params["nb_frames"]
        else:
            nb_frames = acq_params["npoints"]

        return RoiProfilesAcquisitionObject(
            rois=self.roi_profiles.rois,
            controller=self,
            pipeline=self.pipeline,
            npoints=nb_frames,
            ctrl_params=ctrl_params,
        )

    def get_default_chain_parameters(self, scan_params, acq_params):
        try:
            npoints = acq_params["npoints"]
        except KeyError:
            npoints = scan_params["npoints"]

        params = {"npoints": npoints}

        return params


class DetectorStatusController(SamplingCounterController):
    def __init__(self, device):
        super().__init__(device.name, register_counters=False)

        self._lima2 = device._lima2

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        if "expo_time" in parent_acq_params:
            count_time = parent_acq_params["expo_time"]
        else:
            count_time = acq_params["count_time"]

        if "nb_frames" in parent_acq_params:
            nb_frames = parent_acq_params["nb_frames"]
        else:
            nb_frames = acq_params["npoints"]

        return SamplingCounterAcquisitionSlave(
            self,
            ctrl_params=ctrl_params,
            count_time=count_time,
            npoints=nb_frames,
        )

    def read_all(self, *counters):
        status = self._lima2.detector.status()

        values = []
        for cnt in counters:
            values.append(status[cnt.name])
        return values


class IntegratingCounterAcquisitionObject(AcquisitionSlave):
    """Acquisition object for scalar counters (e.g. xpcs fill factor).

    Assumes counters added to it are named according to the expected "stream
    name" that will be fetched from the conductor, and that this stream's
    structured array will have a column of the same name.

    For example, we can add a counter named "fill_factor", knowing that the
    conductor will expose a reduced data stream named "fill_factor", and that
    the rows retrieved when fetching it will have a "fill_factor" column.
    """

    def __init__(
        self,
        controller: "IntegratingCounterController",
        pipeline: services.Pipeline,
        npoints,
        ctrl_params,
    ):
        super().__init__(
            controller,
            npoints=npoints,
            ctrl_params=ctrl_params,
            prepare_once=True,
            start_once=True,
        )

        self.pipeline = pipeline
        """Conductor pipeline services."""

    def reading(self):
        """Launch tasks to fetch and emit statistics for each counter."""

        def fetch_and_emit(counter: Counter):
            """Fetch all rows for a given reduced data channel and emit."""
            # NOTE: assume the counter name corresponds to a valid reduced data
            # stream, and that the fetched structured array has a column of the
            # same name.
            for row in self.pipeline.reduced_data(name=counter.name, channel_idx=0):
                self._counters[counter][0].emit(row[counter.name])

        def on_error(greenlet):
            _logger.error("".join(traceback.format_exception(greenlet.exception)))

        tasks = []
        for counter in self._counters:
            task = gevent.spawn(fetch_and_emit, counter)
            task.link_exception(on_error)
            tasks.append(task)

        gevent.joinall(tasks)

    def prepare(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def trigger(self):
        pass


class IntegratingController(IntegratingCounterController):
    def __init__(
        self,
        name: str,
        pipeline: services.Pipeline,
        master_controller,
    ):
        super().__init__(
            name,  # Automatically prefixed with master_controller name
            master_controller=master_controller,
            register_counters=False,
        )

        self.pipeline = pipeline
        """Conductor pipeline services."""

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        # Avoid RuntimeError: {'acq_params': [{'count_time': ['null value not allowed']}]}
        # when creating children in create_children_acq_obj

        if "nb_frames" in parent_acq_params:
            nb_frames = parent_acq_params["nb_frames"]
        else:
            nb_frames = acq_params["npoints"]

        return IntegratingCounterAcquisitionObject(
            controller=self,
            pipeline=self.pipeline,
            npoints=nb_frames,
            ctrl_params=ctrl_params,
        )

    def get_default_chain_parameters(self, scan_params, acq_params):
        try:
            npoints = acq_params["npoints"]
        except KeyError:
            npoints = scan_params["npoints"]

        params = {"npoints": npoints}

        return params


class ProcessingController(CounterController):
    """
    Processing controller.
    """

    TIMEOUT = 10.0

    @logger
    def __init__(self, device):
        super().__init__(device.name, register_counters=False)

        self._dev = device

    # implements CounterController
    # {
    # Called by scan builder (toolbox) after get_default_chain_parameters
    @logger
    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        """
        Returns an AcquisitionObject instance.

        This function is intended to be used by the `ChainNode`.
        `acq_params`, `ctrl_params` and `parent_acq_params` have to be `dict` (`None` not supported)

        In case a incomplete set of `acq_params` is provided `parent_acq_params` may eventually
        be used to complete `acq_params` before choosing which Acquisition Object needs to be
        instantiated or just to provide all necessary `acq_params` to the Acquisition Object.

        parent_acq_params should be inserted into `acq_params` with low priority to not overwrite
        explicitly provided `acq_params` i.e. by using `setdefault`
        """
        _logger.debug(f"{acq_params} {ctrl_params} {parent_acq_params}")

        # avoid cyclic import
        from bliss.scanning.acquisition.lima2 import Lima2ProcessingSlave

        return Lima2ProcessingSlave(
            self, self.name + ":proc", ctrl_params=ctrl_params, **acq_params
        )

        # Called first by scan builder (toolbox) to get default scan params

    @logger
    def get_default_chain_parameters(self, scan_params, acq_params):
        return {}
