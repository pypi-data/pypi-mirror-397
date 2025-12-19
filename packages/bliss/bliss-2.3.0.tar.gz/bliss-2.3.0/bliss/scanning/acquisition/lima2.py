# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import logging
import gevent
import numpy as np
from glom import glom
from gevent import event
from itertools import repeat
from pathlib import Path

from bliss.scanning.chain import AcquisitionMaster, AcquisitionSlave
from bliss.scanning.channel import Lima2AcquisitionChannel
from bliss.common.os_utils import makedirs
from bliss.controllers.lima2.device import Lima2

from lima2.common.types import FrameInfo

_logger = logging.getLogger("bliss.scans.lima2")


# Logger decorator
def logger(fn):
    def inner(*args, **kwargs):
        _logger.debug(f"Entering {fn.__name__}")
        to_execute = fn(*args, **kwargs)
        _logger.debug(f"Exiting {fn.__name__}")
        return to_execute

    return inner


class Lima2AcquisitionMaster(AcquisitionMaster):
    """
    AcquisitionMaster object for 2D lima detectors.
    Controls the acquisition of images during a BLISS scanning procedure.
    It takes a dictionary of acquisition parameters 'acq_params' that describes
    when and how images will be acquired:

    acq_params keys:
        'acq_nb_frames'    : the number of frames for which a detector is prepared (0 for an infinite number of frames)
        'acq_expo_time'    : the detector exposure time in seconds
        'acq_trigger_mode' : the triggering mode in ['INTERNAL_TRIGGER', 'INTERNAL_TRIGGER_MULTI', 'EXTERNAL_TRIGGER', 'EXTERNAL_TRIGGER_MULTI', 'EXTERNAL_GATE', 'EXTERNAL_START_STOP']
        'acq_mode'         : the acquisition mode in ['SINGLE', 'CONCATENATION', 'ACCUMULATION']
        'prepare_once'     : False if the detector should be prepared before each scan iteration (prepared for 'acq_nb_frames' each time)
        'start_once'       : False if detector.startAcq() should be called at each scan iteration
        'wait_frame_id'    : (optional) A list of frames IDs for which this object should wait before proceeding to the next scan iteration (it could be an iterator too)

    Note: `wait_frame_id` is the frame number to wait for the next sequence in case the synchronisation is base on data.
    i.e: for a mesh with one fast axes (continous), combine with one slow step motor. if you do 20 images per line,
    the wait_frame_id must be equal to :code:`range(0,TOTAL_IMAGE,IMAGE_PER_LINE)`.
    """

    def __init__(self, device, name, ctrl_params=None, **acq_params):
        # ensure that ctrl-params have been completed
        ctrl_params = self.init_ctrl_params(device, ctrl_params)

        self.acq_params = acq_params

        _logger.debug(f"ctrl_params: {ctrl_params} acq_params: {acq_params}")

        nb_frames = self.acq_params["nb_frames"]

        # # deal with 'ONE_FILE_PER_SCAN' mode
        # if ctrl_params.get("saving_frame_per_file") == -1:
        #     ctrl_params["saving_frame_per_file"] = nb_frames

        trigger_type = (
            AcquisitionMaster.SOFTWARE
            if self.acq_params["trigger_mode"] in ["internal", "software"]
            else AcquisitionMaster.HARDWARE
        )

        AcquisitionMaster.__init__(
            self,
            device,
            name=name,
            npoints=nb_frames,
            trigger_type=trigger_type,
            prepare_once=self.acq_params["prepare_once"],
            start_once=self.acq_params["start_once"],
            ctrl_params=ctrl_params,
        )

        self._dev: Lima2 = self.device._dev  # Note self.device is FrameController
        self._lima2 = self._dev._lima2
        self._ready_event = event.Event()
        self._ready_event.set()
        self.__sequence_index = 0

        if self.npoints <= 0:
            # 'infinite' acquisition;
            # supposedly, frame by frame: there are N iterations of 1 frame
            self.__frames_per_iteration_iter = repeat(0)
        else:
            frame_number_range = self.acq_params.pop("wait_frame_id", None)
            if frame_number_range is None:
                # npoints represent the number of frames to be taken;
                # there are N iterations of X frames, N*X=npoints
                if acq_params["prepare_once"]:
                    self.__frames_per_iteration_iter = iter(range(self.npoints))
                else:
                    self.__frames_per_iteration_iter = repeat(self.npoints - 1)
            else:
                self.__frames_per_iteration_iter = iter(frame_number_range)
        self._current_wait_frame_id = None

    @staticmethod
    def get_param_validation_schema():
        _logger.debug("In get_param_validation_schema")
        return {}

    @classmethod
    def validate_params(cls, acq_params, ctrl_params=None):
        # TODO deals with validation later (bypass BlissValidator)
        _logger.debug(
            f"In validate_params ctrl_params: {ctrl_params} acq_params: {acq_params}"
        )
        return acq_params

    @property
    def fast_synchro(self):
        # return self._dev._det.synchro_mode == "TRIGGER"
        return False

    @logger
    def __iter__(self):
        while True:
            try:
                self._current_wait_frame_id = next(self.__frames_per_iteration_iter)
            except StopIteration as e:
                e.args = (
                    self.device.name,
                    *e.args,
                    "Synchronisation error, **wait_frame_id** is wrongly set for this scan",
                )
                raise
            yield self
            if self.parent is None:
                # we have to stop iterations ourselves
                return
            self.__sequence_index += 1

    @logger
    def add_counter(self, counter):
        """Called right after the AcquisitionObject creation"""
        if counter in self._counters:
            return

        self.channels.append(
            Lima2AcquisitionChannel(
                name=f"{self.name}:{counter.name}",
                conductor_hostname=self._lima2.session.hostname,
                conductor_port=self._lima2.session.port,
                source_name=counter.name,
                saving_spec=counter.saving_spec,
                file_only=counter.file_only,
            )
        )

        _logger.debug(f"Created image channel {self.name}:{counter.name}")

        self._counters[counter].append(self.channels[-1])

    @logger
    @property
    def save_flag(self):
        return bool(self.channels)

    @logger
    def prepare(self):
        # should be moved to scan framework
        if self.__sequence_index > 0 and self.prepare_once:
            return

        _logger.debug(f"-> ctrl_params: {self.ctrl_params}")
        _logger.debug(f"-> acq_params: {self.acq_params}")

        # Update parameters before prepare
        for p in [self.ctrl_params["ctrl"], self.ctrl_params["recvs"]]:
            p["acq"]["nb_frames"] = self.acq_params["nb_frames"]
            p["acq"]["expo_time"] = int(self.acq_params["expo_time"] * 1e6)
            p["acq"]["latency_time"] = int(self.acq_params.get("latency_time", 0) * 1e6)
            p["acq"]["trigger_mode"] = self.acq_params["trigger_mode"]
            p["acq"]["nb_frames_per_trigger"] = self.acq_params.get(
                "nb_frames_per_trigger", 1
            )

        # Update channel parameters from saving parameters
        nb_saving = 0
        for channel in self.channels:
            if channel.saving_spec is not None:
                saving_params = glom(self.ctrl_params, channel.saving_spec)
                if not isinstance(saving_params, list):
                    saving_params = [saving_params]

                if self.acq_params["is_saving"] is True:
                    for s in saving_params:
                        if s["enabled"]:
                            nb_saving += 1
                            # Update saving parameters first
                            s.update(
                                {
                                    "base_path": self.acq_params["saving_directory"],
                                    "filename_prefix": self.acq_params["saving_prefix"]
                                    + channel.short_name,
                                    "nx_detector_name": self.name,
                                }
                            )
                else:
                    for s in saving_params:
                        s.update({"enabled": False})

        # If saving required, check that at least one saving channel is enabled
        if self.acq_params["is_saving"] is True and nb_saving == 0:
            _logger.error(
                f"LIMA2 {self.name} saving requested but no saving channel enabled"
            )
            raise RuntimeError(
                f"LIMA2 {self.name} saving requested but no saving channel enabled"
            )

        self.acq_uuid = self._dev.prepare(
            self.ctrl_params["ctrl"],
            self.ctrl_params["recvs"],
            self.ctrl_params["procs"],
        )

        frame_infos = self._lima2.pipeline.frame_channels(uuid=self.acq_uuid)
        master_files = self._lima2.pipeline.master_files(uuid=self.acq_uuid)

        # Update channel description with the newly constructed processing
        for channel in self.channels:
            assert type(channel) is Lima2AcquisitionChannel, f"{type(channel)}"

            info: FrameInfo = frame_infos[channel.short_name]

            channel.finalize(
                uuid=str(self.acq_uuid),
                shape=(info.num_channels, info.height, info.width),
                dtype=info.pixel_type,
                master_file=master_files.get(channel.short_name, None),
            )

        _logger.debug(f"state {self._lima2.acquisition.state()}")

        self._nb_triggers = 0

    @logger
    def start(self):
        # ! STARTS must be called independently of the trigger_type !
        # if self.trigger_type == AcquisitionMaster.SOFTWARE and self.parent:
        #     # otherwise top master trigger would never be called
        #     return

        if self.__sequence_index > 0 and self.start_once:
            # run start only for the first sequence
            if self.trigger_type == AcquisitionMaster.SOFTWARE and not self.parent:
                # We dont have a top master
                self.trigger()
            return

        self._dev.start()

        self.spawn_reading_task(rawlink_event=self._ready_event)

        _logger.debug(f"state {self._lima2.acquisition.state()}")

    @logger
    def stop(self):
        self._dev.stop()

    # def trigger_ready(self):
    #     return True

    @logger
    def wait_ready(self):
        _logger.debug("ready event wait START")
        self._ready_event.wait()
        _logger.debug("ready event wait END")
        self._ready_event.clear()
        _logger.debug("ready event CLEAR")

    @logger
    def trigger(self):
        self.trigger_slaves()

        self._nb_triggers += 1

        self._dev.trigger()

    @logger
    def set_device_saving(self, directory, prefix, force_no_saving=False):
        """Called by the writer when preparing the scan"""
        if self.save_flag and not force_no_saving:
            self.acq_params["is_saving"] = True
            self.acq_params["saving_directory"] = directory

            # if path is valid, create directory (if it doesnt exist yet)
            if not Path(directory).exists():
                makedirs(directory, exist_ok=True)

            self.acq_params.setdefault("saving_prefix", prefix)
        else:
            self.acq_params["is_saving"] = False

    def _emit_status(self, status, processing_progress: int):
        progress_keys = ["nb_frames_acquired", "nb_frames_xferred"]
        self.emit_progress_signal(
            {"state": status["state"]}
            | {k: status[k] for k in progress_keys}
            | {"processed": processing_progress}
        )

        # Send progress to Lima2Client.update()
        for ch in self.channels:
            assert type(ch) is Lima2AcquisitionChannel, f"{type(ch)}"
            progress = self._lima2.pipeline.progress(
                channel=ch.short_name, uuid=self.acq_uuid
            )
            ch.emit(np.uint32(progress))

    @logger
    def reading(self):
        """Gather and emit lima status while camera is running (acq_state and last image info).
        Also sets the '_ready_event' when it is valid to proceed to the next scan iteration.
        For each 'prepare', camera is configured for the acquisition of 'acq_nb_frames'
        and this method exists when all 'acq_nb_frames' have been acquired.
        This method is automatically (re)spwaned after each start/trigger call (if not already alive).
        """
        _logger.debug("reading: started")

        last_nb_frames = 0

        while self._lima2.acquisition.running() or self._lima2.pipeline.running():
            new_image_acquired = False

            state = self._lima2.acquisition.state()
            nfa = self._lima2.acquisition.nb_frames_acquired()
            nfx = self._lima2.acquisition.nb_frames_xferred()
            nfp = self._lima2.pipeline.progress(uuid=self.acq_uuid)

            _logger.debug(f"reading: {state=} {nfa=} {nfx=} {nfp=}")

            # Use the max of nb_frames_acquired and nb_frames_xferred as progress indicator
            nb_frames = max(nfa, nfx)
            if nb_frames > last_nb_frames:
                new_image_acquired = True
                last_nb_frames = nb_frames

            self._emit_status(
                {
                    "state": state,
                    "nb_frames_acquired": max(nfa, nfx),
                    "nb_frames_xferred": nfx,
                },
                nfp,
            )

            # Check that new images were acquired
            if new_image_acquired:
                # Check if next iteration is allowed
                if not self._ready_event.is_set():
                    if self.prepare_once:
                        _logger.debug(
                            f"nb_frames {nb_frames} / {self._current_wait_frame_id}"
                        )
                        if nb_frames >= self._current_wait_frame_id:
                            self._ready_event.set()
                            _logger.debug("set ready event")
                else:
                    _logger.debug("ready event is set")

            # Sleep between [10, 100] milliseconds depending on expo time
            gevent.sleep(min(0.1, max(self.acq_params["expo_time"] / 10.0, 0.01)))

        # Emit final up-to-date status
        state = self._lima2.acquisition.state()
        nfa = self._lima2.acquisition.nb_frames_acquired()
        nfx = self._lima2.acquisition.nb_frames_xferred()
        nfp = self._lima2.pipeline.progress(uuid=self.acq_uuid)

        self._emit_status(
            {
                "state": state,
                "nb_frames_acquired": max(nfa, nfx),
                "nb_frames_xferred": nfx,
            },
            nfp,
        )

        if self._lima2.acquisition.failed():
            # Report errors and raise
            acq_errors = self._lima2.acquisition.errors()
            proc_errors = self._lima2.pipeline.errors()

            msg = f"\n\nLIMA2 {self.name} is in Fault state. Errors:"
            if acq_errors:
                msg += "\n- " + "\n- ".join(acq_errors)
            if proc_errors:
                msg += "\n- " + "\n- ".join(proc_errors)
            msg += f"\n\nUse {self.name}.reset() to attempt recovery.\n\n"
            _logger.error(msg)
            raise RuntimeError(msg)

        _logger.debug("reading: finished")

    def get_acquisition_metadata(self, timing=None):
        """
        Returns time-dependent meta data related to this device.
        """
        tmp_dict = super().get_acquisition_metadata(timing=timing)
        if timing == self.META_TIMING.END:
            if tmp_dict is None:
                tmp_dict = dict()

            # TODO: save all the information (currently, saving all ctrl_params is not suppported by the NxWriter)
            tmp_dict["acq_params"] = self.ctrl_params["ctrl"]

            # from copy import deepcopy
            # tmp_dict = deepcopy(self.ctrl_params)

        return tmp_dict


class Lima2ProcessingSlave(AcquisitionSlave):
    pass
