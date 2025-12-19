# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numexpr
from bliss import global_map
from bliss.config.static import ConfigNode
from bliss.common.counter import Counter, CalcCounter
from bliss.controllers.counter import CalcCounterController
from bliss.controllers.mosca.counters import (
    SpecCounter,
    RoiCounter,
    StatCounter,
)


class CorrRoiCounter(CalcCounter):
    pass


class CorrSpecCounter(CalcCounter):
    pass


class SumRoiCounter(CalcCounter):
    pass


class SumSpecCounter(CalcCounter):
    pass


class StatCorrCalcCC(CalcCounterController):
    """Apply a correction formula to given input counters (rois or spectra).
    Correction formula can use MCA statistics counters and any
    other counter declared as an external counter in the YML configuration.
    example: 'raw / (1-trigger_livetime/realtime) / iodet'

    Formula is automatically applied per MCA channel (aka detector).
    """

    def __init__(
        self,
        name: str,
        config: ConfigNode | dict,
        input_type: type[RoiCounter] | type[SpecCounter],
        output_type: type[CorrRoiCounter] | type[SumSpecCounter],
        stat_counters: list[StatCounter],
        calc_formula: str = "",
    ) -> None:

        super().__init__(name=name, config=config)

        self._input_type = input_type
        self._output_type = output_type
        self._calc_formula = calc_formula

        self._chan_suffix: str = "_det"
        self._corr_suffix: str = "corr"
        self._external_counters: dict[str, Counter] = {}

        # === External counters
        ext_cnts: ConfigNode | None = config.get("external_counters")
        if ext_cnts:
            self._external_counters = ext_cnts.to_dict()

        # === StatCounters
        self._stat_counters: list[StatCounter] = []
        stat_keys = []
        for cnt in stat_counters:
            if isinstance(cnt, StatCounter):
                self._stat_counters.append(cnt)
                statkey, _, _ = cnt.name.rpartition(self._chan_suffix)
                if statkey:
                    stat_keys.append(statkey)

        self._stat_keys = list(dict.fromkeys(stat_keys))  # ordered set

    def _build_output_name(self, input_name: str) -> str:
        head, sep, tail = input_name.rpartition(self._chan_suffix)
        return f"{head}_{self._corr_suffix}{sep}{tail}"

    def build_counters(self, config) -> None:
        # replaced by self.update_counters
        pass

    def update_counters(self, input_counters: list[Counter]) -> None:

        # Unregister previous outputs
        self._global_map_unregister()

        # === Build inputs list and output counters
        self._counters: dict[str, Counter] = {}
        self._tags: dict[str, str] = {}
        self._input_counters: list[Counter] = []
        self._output_counters: list[CalcCounter] = []

        if self.calc_formula:
            for cnt in input_counters:
                if isinstance(cnt, self._input_type):
                    if cnt.det_num is not None:
                        cname = cnt.name
                        self._tags[cname] = cname
                        self._input_counters.append(cnt)

                        cntout_name = self._build_output_name(cname)
                        cntout = self._output_type(cntout_name, self, shape=cnt.shape)
                        self._tags[cntout_name] = cntout_name
                        self._output_counters.append(cntout)

                        global_map.register(cntout, parents_list=["counters"])

            for cnt in self._stat_counters:
                self._tags[cnt.name] = cnt.name
                self._input_counters.append(cnt)

            for tag, cnt in self._external_counters.items():
                if tag in self.calc_formula:
                    self._tags[cnt.name] = tag
                    self._input_counters.append(cnt)

    @property
    def tags(self) -> dict[str, str]:
        return self._tags

    @property
    def calc_formula(self) -> str:
        return self._calc_formula

    @calc_formula.setter
    def calc_formula(self, formula: str | None) -> None:
        if formula is None:
            formula = ""

        if not isinstance(formula, str):
            raise ValueError(
                "formula must be a string, ex: 'roi / (1-deadtime) / iodet' "
            )

        formula = formula.strip()

        if formula:

            # test formula validity
            local_dict = {"raw": 1, "roi": 1}
            for stat in self._stat_keys:
                local_dict[stat] = 1
            for tag in self._external_counters:
                local_dict[tag] = 1
            try:
                numexpr.evaluate(formula, global_dict={}, local_dict=local_dict)
            except Exception as e:
                raise ValueError(
                    f"formula not valid ({e}), ensure variables are in {list(local_dict.keys())}"
                )

        self._calc_formula = formula

    def calc_function(self, input_dict: dict[str, float]) -> dict[str, float]:
        output_dict = {}
        local_dict = input_dict.copy()
        for cnt in self._input_counters:
            if isinstance(cnt, self._input_type):
                cname = cnt.name
                detchan = cnt.det_num
                cntout_name = self._build_output_name(cname)

                local_dict["roi"] = input_dict[cname]
                local_dict["raw"] = input_dict[cname]

                for stat in self._stat_keys:
                    local_dict[stat] = input_dict[
                        f"{stat}{self._chan_suffix}{detchan:02d}"
                    ]

                output_dict[cntout_name] = numexpr.evaluate(
                    self.calc_formula, global_dict={}, local_dict=local_dict
                ).astype(float)

        return output_dict


class SumCalcCC(CalcCounterController):
    def __init__(
        self,
        name: str,
        input_type: type[CorrRoiCounter] | type[CorrSpecCounter],
        output_type: type[SumRoiCounter] | type[SumRoiCounter],
    ) -> None:

        self._input_type = input_type
        self._output_type = output_type
        self._chan_suffix: str = "_det"
        self._sum_suffix: str = "sum"

        super().__init__(name, {})

    def _build_output_name(self, input_name: str) -> str:
        head, _, _ = input_name.rpartition(self._chan_suffix)
        return f"{head}_{self._sum_suffix}"

    @property
    def tags(self) -> dict[str, str]:
        return self._tags

    def build_counters(self, config) -> None:
        # superseded by update_counters
        pass

    def update_counters(self, input_counters: list[Counter]) -> None:

        # Unregister previous outputs
        self._global_map_unregister()

        # === Build inputs list and output counters
        self._counters: dict[str, Counter] = {}
        self._tags: dict[str, str] = {}
        self._input_counters: list[Counter] = []
        self._output_counters: list[CalcCounter] = []

        self._out2in: dict[str, list[str]] = {}
        tmp_out2in: dict[str, list[Counter]] = {}
        for cntin in input_counters:
            if isinstance(cntin, self._input_type):
                cntout_name = self._build_output_name(cntin.name)
                tmp_out2in.setdefault(cntout_name, []).append(cntin)

        # create sum counters and store inputs
        # only if there are at least 2 roi_corr to sum
        for cntout_name in tmp_out2in:
            if len(tmp_out2in[cntout_name]) > 1:
                shape = tmp_out2in[cntout_name][0].shape
                cntout = self._output_type(cntout_name, self, shape=shape)
                self._tags[cntout_name] = cntout_name
                self._output_counters.append(cntout)
                self._out2in[cntout_name] = []
                for cntin in tmp_out2in[cntout_name]:
                    self._tags[cntin.name] = cntin.name
                    self._input_counters.append(cntin)
                    self._out2in[cntout_name].append(cntin.name)

                global_map.register(cntout, parents_list=["counters"])

    def calc_function(self, input_dict: dict[str, float]) -> dict[str, float]:
        output_dict: dict[str, float] = {}
        for cntout_name, inputs in self._out2in.items():
            output_dict[cntout_name] = 0
            for cntin_tag in inputs:
                output_dict[cntout_name] += input_dict[cntin_tag]
        return output_dict
