# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from bliss import global_map
from bliss.config.static import ConfigNode
from bliss.common.protocols import CounterContainer
from bliss.common.counter import Counter, CalcCounter, SoftCounter
from bliss.common.utils import autocomplete_property, IterableNamespace
from bliss.scanning.chain import ChainNode, AcquisitionObject
from bliss.scanning.acquisition.counter import SamplingCounterAcquisitionSlave
from bliss.scanning.acquisition.counter import IntegratingCounterAcquisitionSlave

from bliss.scanning.acquisition.calc import (
    CalcCounterChainNode,
    CalcCounterAcquisitionSlave,
)
from bliss.common.protocols import counter_namespace


class CounterController(CounterContainer):
    def __init__(
        self,
        name: str,
        master_controller: "CounterController | None" = None,
        register_counters: bool = True,
    ) -> None:

        self.__name = name
        self.__master_controller = master_controller
        self._counters: dict[str, Counter] = {}

        if register_counters:
            global_map.register(self, parents_list=["counters"])

    def _global_map_unregister(self) -> None:
        global_map.unregister(self)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def fullname(self) -> str:
        if self._master_controller is None:
            return self.name
        else:
            return f"{self._master_controller.fullname}:{self.name}"

    @property
    def _master_controller(self) -> "CounterController | None":
        return self.__master_controller

    @autocomplete_property
    def counters(self) -> IterableNamespace:
        return counter_namespace(self._counters)

    def create_counter(self, counter_class: type[Counter], *args, **kwargs) -> Counter:
        counter = counter_class(*args, controller=self, **kwargs)
        return counter

    # --------------------- NOT IMPLEMENTED METHODS  ------------------------------------

    def get_acquisition_object(
        self, acq_params: dict, ctrl_params: dict, parent_acq_params: dict
    ) -> AcquisitionObject:
        """
        Returns an Acquisition object instance.

        This function is intended to be used through by the `ChainNode`.
        `acq_params`, `ctrl_params` and `parent_acq_params` have to be `dict` (`None` not supported)

        In case a incomplete set of `acq_params` is provided `parent_acq_params` may eventually
        be used to complete `acq_params` before choosing which Acquisition Object needs to be
        instantiated or just to provide all necessary `acq_params` to the Acquisition Object.

        parent_acq_params should be inserted into `acq_params` with low priority to not overwrite
        explicitly provided `acq_params` i.e. by using `setdefault`

        Example:

        .. code-block:: python

            if "acq_expo_time" in parent_acq_params:
                acq_params.setdefault("count_time", parent_acq_params["acq_expo_time"])
        """
        raise NotImplementedError

    def get_default_chain_parameters(self, scan_params: dict, acq_params: dict) -> dict:
        """return completed acq_params with missing values guessed from scan_params
        in the context of default chain i.e. step-by-step scans"""
        raise NotImplementedError

    # --------------------- CUSTOMIZABLE METHODS  ------------------------------------
    def create_chain_node(self) -> ChainNode:
        return ChainNode(self)

    def get_current_parameters(self) -> dict | None:
        """Should return an exhaustive dict of parameters that will be send
        to the hardware controller at the beginning of each scan.
        These parametes may be overwritten by scan specifc ctrl_params
        """
        return None

    def apply_parameters(self, parameters: dict) -> None:
        pass


class SamplingCounterController(CounterController):
    def __init__(
        self,
        name: str,
        master_controller: CounterController | None = None,
        register_counters: bool = True,
    ) -> None:
        assert master_controller is not self
        super().__init__(
            name,
            master_controller=master_controller,
            register_counters=register_counters,
        )
        # by default maximum sampling frequency during acquisition loop = 1 Hz
        self.__max_sampling_frequency: int | float | None = 1

    @property
    def max_sampling_frequency(self) -> int | float | None:
        """Maximum sampling frequency in acquisition loop (Hz) (None -> no limit)"""
        return self.__max_sampling_frequency

    @max_sampling_frequency.setter
    def max_sampling_frequency(self, freq: int | float | None) -> None:
        """Maximum sampling acquisition frequency setter.

        freq = <int, float> -> set the frequency
        freq = None         -> means no limit (maximum frequency)
        """
        if freq and not isinstance(freq, (float, int)):
            raise ValueError("Max frequency should be a float number or None")
        if freq == 0:
            raise ValueError("Max frequency should be not zero")
        self.__max_sampling_frequency = freq

    def get_acquisition_object(
        self, acq_params: dict, ctrl_params: dict, parent_acq_params: dict
    ) -> SamplingCounterAcquisitionSlave:
        return SamplingCounterAcquisitionSlave(
            self, ctrl_params=ctrl_params, **acq_params
        )

    def get_default_chain_parameters(self, scan_params: dict, acq_params: dict) -> dict:

        try:
            count_time = acq_params["count_time"]
        except KeyError:
            count_time = scan_params["count_time"]

        try:
            npoints = acq_params["npoints"]
        except KeyError:
            npoints = scan_params["npoints"]

        params = {"count_time": count_time, "npoints": npoints}

        return params

    def read_all(self, *counters: Counter) -> list:
        """Return the values of the given counters as a list.

        If possible this method should optimize the reading of all counters at once.
        """
        values = []
        for cnt in counters:
            values.append(self.read(cnt))
        return values

    def read(self, counter: Counter):
        """Return the value of the given counter"""
        raise NotImplementedError


class IntegratingCounterController(CounterController):
    def __init__(
        self,
        name: str = "integ_cc",
        master_controller: CounterController = None,
        register_counters: bool = True,
    ) -> None:
        super().__init__(
            name,
            master_controller=master_controller,
            register_counters=register_counters,
        )

    def get_acquisition_object(
        self, acq_params: dict, ctrl_params: dict, parent_acq_params: dict
    ) -> IntegratingCounterAcquisitionSlave:
        return IntegratingCounterAcquisitionSlave(
            self, ctrl_params=ctrl_params, **acq_params
        )

    def get_default_chain_parameters(self, scan_params: dict, acq_params: dict) -> dict:
        try:
            count_time = acq_params["count_time"]
        except KeyError:
            count_time = scan_params["count_time"]

        params = {"count_time": count_time}

        if self._master_controller is None:
            try:
                npoints = acq_params["npoints"]
            except KeyError:
                npoints = scan_params["npoints"]

            params["npoints"] = npoints

        return params

    def get_values(self, from_index: int, *counters: Counter) -> list[list]:
        """
        Returns values from counters during the acquisition reading loop.

        This function is called by the acq_obj from a greenlet.
        It is triggered every 100ms until the `npoints` are fetched.

        If the function yet dont have the data, an empty list can be returned

        .. code-block:: python

            if not_ready:
                return [[]] * len(counters)

        Attributes:
            from_index: Index of the first scan point to retrive
            counters: The list of counters to read
        Returns:
            A list of list of data for each counters, each data must have the
            same size
        """
        raise NotImplementedError


class CalcCounterController(CounterController):
    def __init__(
        self, name: str, config: ConfigNode | dict, register_counters: bool = True
    ) -> None:

        super().__init__(name, register_counters=False)

        self._config = config
        self._input_counters: list[Counter] = []
        self._output_counters: list[CalcCounter] = []
        self._counters: dict[str, CalcCounter] = {}
        self._tags: dict[str, str] = {}

        self.build_counters(config)

        if register_counters:
            for counter in self.outputs:
                global_map.register(counter, parents_list=["counters"])

    def _global_map_unregister(self) -> None:
        for counter in self.outputs:
            global_map.unregister(counter)

    def get_acquisition_object(
        self,
        acq_params: dict,
        ctrl_params: dict,
        parent_acq_params: dict,
        acq_devices: list[AcquisitionObject],
    ) -> CalcCounterAcquisitionSlave:
        return CalcCounterAcquisitionSlave(
            self, acq_devices, acq_params, ctrl_params=ctrl_params
        )

    def get_default_chain_parameters(self, scan_params: dict, acq_params: dict) -> dict:
        if acq_params.get("npoints") is None:
            acq_params["npoints"] = scan_params["npoints"]

        return acq_params

    def create_chain_node(self) -> CalcCounterChainNode:
        return CalcCounterChainNode(self)

    @property
    def tags(self) -> dict[str, str]:
        updated_tags = {}
        # update dictionary with aliases
        for name, cnt_tags in self._tags.items():
            alias = global_map.aliases.get_alias(name)
            if alias:
                updated_tags[alias] = cnt_tags
            updated_tags[name] = cnt_tags
        self._tags = updated_tags
        return self._tags

    def build_counters(self, config: ConfigNode | dict) -> None:
        """Build the CalcCounters from config.

        'config' is a dict with 2 keys: 'inputs' and 'outputs'.
        'config["inputs"]'  is a list of dict:  [{"counter":$cnt1, "tags": foo }, ...]
        'config["outputs"]' is a list of dict:  [{"name":out1, "tags": calc_data_1 }, ...]
        If the 'tags' is not found, the counter name will be used instead.
        """
        for cnt_conf in config.get("inputs"):
            cnt = cnt_conf.get("counter")
            if isinstance(cnt, Counter):
                tags = cnt_conf.get("tags", cnt.name)
                self._tags[cnt.name] = tags
                self._input_counters.append(cnt)
            else:
                raise ValueError(
                    f"CalcCounterController's input must be a counter but received: {cnt}"
                )

        for cnt_conf in config.get("outputs"):
            cnt_name = cnt_conf.get("name")
            if cnt_name:
                dim = cnt_conf.get("dim")
                if dim is None:
                    shape = cnt_conf.get("shape", tuple())
                else:
                    shape = cnt_conf.get("shape", (-1,) * dim)
                    if len(shape) != dim:
                        raise ValueError(
                            f"Wrong config for CalcCounterController's output '{cnt_name}': shape and dim mismatch (when using 'shape', 'dim' can be omitted)"
                        )

                unit = cnt_conf.get("unit")
                dtype = cnt_conf.get("dtype")
                cnt = CalcCounter(
                    cnt_name, controller=self, dtype=dtype, shape=shape, unit=unit
                )
                tags = cnt_conf.get("tags", cnt.name)
                self._tags[cnt.name] = tags
                self._output_counters.append(cnt)

    @property
    def inputs(self) -> IterableNamespace:
        return counter_namespace(self._input_counters)

    @property
    def outputs(self) -> IterableNamespace:
        return counter_namespace(self._output_counters)

    @autocomplete_property
    def counters(self) -> IterableNamespace:
        """Return all counters (i.e. the counters of this CounterController and sub counters)"""

        counters = {cnt.name: cnt for cnt in self.outputs}
        for cnt in self.inputs:
            counters[cnt.name] = cnt
            if isinstance(cnt, CalcCounter):
                counters.update(
                    {cnt.name: cnt for cnt in cnt._counter_controller.counters}
                )
        return counter_namespace(counters)

    def calc_function(self, input_dict: dict) -> dict:
        raise NotImplementedError


class SoftCounterController(SamplingCounterController):
    def __init__(
        self, name: str = "soft_counter_controller", register_counters: bool = True
    ) -> None:
        super().__init__(name, register_counters=True)

    def read(self, counter: SoftCounter):
        return counter.apply(counter.get_value())
