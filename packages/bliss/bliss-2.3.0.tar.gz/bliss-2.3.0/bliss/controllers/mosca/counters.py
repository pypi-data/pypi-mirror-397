# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numpy
from bliss.common.counter import Counter
from bliss.controllers.counter import CounterController
from bliss.controllers.mosca.rois import McaRoi


class MoscaCounter(Counter):
    def __init__(
        self,
        name: str,
        controller: CounterController,
        unit: str | None = None,
    ) -> None:

        super().__init__(name=name, controller=controller, unit=unit)

    @property
    def det_num(self) -> int | None:
        """number (aka channel_alias) of the detector associated to this counter"""
        raise NotImplementedError


class SpecCounter(MoscaCounter):
    def __init__(
        self,
        name: str,
        data_index: int,
        det_num: int,
        controller: CounterController,
        unit: str | None = None,
    ) -> None:

        super().__init__(name=name, controller=controller, unit=unit)

        self._data_index = data_index
        self._det_num = det_num

    @property
    def data_index(self) -> int:
        """index of the spectrum data inside the data array provided by Mosca server (see proxy.getData)"""
        return self._data_index

    @property
    def det_num(self) -> int:
        """number (aka channel_alias) of the detector associated to this counter"""
        return self._det_num

    @property
    def dtype(self):
        return numpy.uint32

    @property
    def shape(self):
        return (self._counter_controller._mca._spectrum_size,)

    def __info__(self) -> str:
        info_str = super().__info__()
        info_str += f" spectrum size: {self.shape[0]}\n"
        return info_str


class RoiCounter(MoscaCounter):
    """A counter for ROI data"""

    def __init__(
        self,
        mca_roi: McaRoi,
        controller: CounterController,
        unit: str | None = None,
    ) -> None:

        super().__init__(name=mca_roi.name, controller=controller, unit=unit)

        self._mca_roi = mca_roi

    @property
    def fullname(self) -> str:
        """A unique name within the session scope.

        Modified standard implementation by adding 'roi':
        `[<master_controller_name>]:[<controller_name>]:roi:<counter_name>`
        """
        args = []
        if self._counter_controller._master_controller is not None:
            args.append(self._counter_controller._master_controller.name)
        args.append(self._counter_controller.name)
        args.append("roi")
        args.append(self.name)
        return ":".join(args)

    @property
    def roi(self) -> McaRoi:
        return self._mca_roi

    @property
    def det_num(self) -> int | None:
        """number (aka channel_alias) of the detector associated to this counter"""
        chan = self._mca_roi.channel
        # only consider rois with a single channel value (i.e. ignore channel == -1  or == (start, stop) )
        if isinstance(chan, int):
            if chan >= 0:
                return chan

        return None

    @property
    def dtype(self):
        return numpy.int64

    @property
    def shape(self):
        return ()

    def __info__(self) -> str:
        info_str = super().__info__()
        info_str += f" roi: [{self.roi.start}:{self.roi.stop}]\n"
        info_str += f" channel: {self.roi.channel}\n"
        return info_str


class StatCounter(MoscaCounter):
    """A counter for statistics data"""

    def __init__(
        self,
        name: str,
        label_index: int,
        data_index: int,
        det_num: int,
        controller: CounterController,
        unit=None,
    ) -> None:

        super().__init__(name=name, controller=controller, unit=unit)

        self._label_index = label_index
        self._data_index = data_index
        self._det_num = det_num

    @property
    def label_index(self) -> int:
        """index of this statistic type among statistics names list (see proxy.metadata_labels)"""
        return self._label_index

    @property
    def data_index(self) -> int:
        """index of the statistic data inside the data array provided by Mosca server (see proxy.getMetadataValues)"""
        return self._data_index

    @property
    def det_num(self) -> int:
        """number (aka channel_alias) of the detector associated to this counter"""
        return self._det_num

    @property
    def dtype(self):
        return numpy.float64

    @property
    def shape(self):
        return ()

    def __info__(self) -> str:
        info_str = super().__info__()
        return info_str
