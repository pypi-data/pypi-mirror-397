# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.


"""
Class FilterSet_Blade serves to control the blade filterset like model on ID10
a motor driven blades with up to 6 blades slots for attenuating the beam intensity.

Filters can be configured with only material and thickness then the density will be the theoric one
othewise one can set an density (g/cm3) or a pair of transmission(range [0-1]) / energy (keV).

Example of yml configuration files:

With NO density:
---------------

- name: filtW0
  package: bliss.common.auto_filter.FilterSet_Blade
  class: FilterSet_Blade
  rotation_axis: $att1
  filters:
    - name:Cu_0
      position: 0
      material: Cu
      thickness: 0
    - name:Cu_1
      position: 1
      material: Cu
      thickness: 0.04673608
    - name:Cu_2
      position: 2
      material: Cu
      thickness: 0.09415565
    - name:Cu_3
      position: 3
      material: Cu
      thickness: 0.14524267
    - name:Cu_4
      position: 4
      material: Cu
      thickness: 0.1911693
    - name:Cu_5
      position: 5
      material: Cu
      thickness: 0.24215921
    - name:Cu_6
      position: 6
      material: Cu
      thickness: 0.27220901
    - name:Cu_7
      position: 7
      material: Cu
      thickness: 0.3227842

With Density:
-------------
- name: filtW0
  package: bliss.common.auto_filter.FilterSet_Blade
  class: FilterSet_Blade
  rotation_axis: $att1
  filters:
    - name:Cu_0
      position: 0
      material: Cu
      thickness: 0
      density: 8.94

    - name:Mo_1
      position: 1
      material: Mo
      thickness: 0.055
      density: 10.22

With pairs transmission/energy:
------------------------------

- name: filtW0
  package: bliss.common.auto_filter.FilterSet_Blade
  class: FilterSet_Blade
  rotation_axis: $att1
  filters:
    - name:Ag_0
      position: 0
      material: Ag
      thickness: 0.1
      transmission: 0.173
      energy: 16

    - name:Ag_1
      position: 1
      material: Ag
      thickness: 0.2
      transmission: 0.0412
      energy: 16

"""

import numpy as np

from functools import reduce
from itertools import product


from bliss.config.settings import SimpleSetting
from bliss.common.auto_filter.filterset import (
    FilterSet,
    prepare_compounds,
    calc_transmissions,
)
from bliss.common.standard import _move


class Blade:
    def __init__(self, config):
        # check some config
        self._rotation_axis = config.get("rotation_axis")
        self._foils = [x.to_dict() for x in config.get("foils", [])]

        self._active_foil = SimpleSetting(
            f"{self._rotation_axis.name}:active_foil", default_value=0
        )

        prepare_compounds(self._foils)

        self.home()

    def __info__(self):
        info_list = []
        info_list.append(f" - Rotation axis: {self._rotation_axis.name}")
        info_list.append(" - Foil Pos.        Mat. Thickness")
        info_list.append("   -------------------------------------")
        for idx, foil in enumerate(self._foils):
            info_list.append(
                f"   {idx:<4} {foil['pos_in']:>4} <-> {foil['pos_out']:<4} {foil['material']:<4} {foil['thickness']:10.8f}"
            )
        return "\n".join(info_list)

    def _prepare_compounds(self):
        """Create the Compound object that will be used for calculating the transmission"""
        prepare_compounds(self._foils)

    def _calc_transmissions(self, energy):
        """
        Calculate the transmission factors for the filters for the given energy
        """
        calc_transmissions(self._foils, energy)

    @property
    def nb_foils(self):
        return len(self._foils)

    @property
    def active_foil(self):
        return self._active_foil.get()

    @active_foil.setter
    def active_foil(self, active_foil):
        self._active_foil.set(active_foil)

    def home(self):
        """
        Move the blade position to the out position of the current selected foil
        """
        self._rotation_axis.move(self._foils[self.active_foil]["pos_out"])

    def set_filter(self, filter_id):
        """
        Set the filter, for a blade it moves to a position
        """
        if filter_id is not None:
            # self._rotation_axis.move(self._foils[self.active_foil]["pos_in"])
            target_pos = self._foils[self.active_foil]["pos_in"]
        else:
            # self._rotation_axis.move(self._foils[self.active_foil]["pos_out"])
            target_pos = self._foils[self.active_foil]["pos_out"]

        return (self._rotation_axis, target_pos)

    def get_filter(self):
        """
        Return the current filter index (or its negative for the out position).
        None is return if the axis position does not correspond to the
        defined positions
        """
        tolerance = self._rotation_axis.tolerance
        position = self._rotation_axis.position
        found_index = None
        for idx, foil in enumerate(self._foils):
            if abs(position - foil["pos_in"]) <= tolerance:
                found_index = idx
                break
            if abs(position - foil["pos_out"]) <= tolerance:
                found_index = None
                break

        try:
            return found_index
        except NameError:
            raise ValueError(
                f"The Blade on motor ({self._rotation_axis.name}) position is {position:.4f}\n        Please move it to a filter position"
            )

    def get_transmission(self, filter_id):
        """
        Return the transmission of filter filter_id
        """
        if filter_id is not None:
            trans = self._foils[filter_id]["transmission_calc"]
        else:
            trans = 1.0
        return trans


class FilterSet_Blade(FilterSet):
    def __init__(self, name, config):
        # get filters from config
        config_blades = config.get("filters")

        self._blades = [Blade(cfg) for cfg in config_blades]

        # never forget to call grandmother !!!
        super().__init__(name, config)

    def __info__(self):
        self._calc_transmissions()
        info_str = f"\nCurrent filter = {self.index}, transmission = {self.transmission:.5g} @ {self.energy:.5g} keV"

        info_str += f"\nActive foils  = {self.active_foils}"
        info_str += "\nCombined foils"
        info_str += (
            f"\n   ID    Combinations            Transm. @ {self._last_energy:.5g} keV:"
        )

        info_str += "\n   -----------------------------------------------------"
        for i, filter in enumerate(self.get_filters()):
            filters = self._decode(filter["position"])
            filters_repr = " ".join([f"{repr(f):<4}" for f in filters])
            info_str += f"\n   {i + 1:<5} [{filters_repr:<18}]    {filter['transmission_calc']:.5g}"

        info_str += f"\n\nAvailable blades = {self.nb_blades}"
        for blade in self._blades:
            blade_info = []
            blade_info.append(f"\n - Rotation axis: {blade._rotation_axis.name}")
            blade_info.append(
                f"   Foil Pos.          Mat. Thickness    Transm. @ {self._last_energy:.5g} keV:"
            )
            blade_info.append(
                "   -----------------------------------------------------"
            )
            for idx, filter in enumerate(blade._foils):
                blade_info.append(
                    f"   {idx:<4} {filter['pos_in']:>4} <-> {filter['pos_out']:<4} {filter['material']:<4} {filter['thickness']:10.8f}   {filter['transmission_calc']:.5g}"
                )
            info_str += "\n" + "\n".join(blade_info)

        return info_str

    @property
    def nb_blades(self):
        return len(self._blades)

    @property
    def active_foils(self):
        return [blade.active_foil for blade in self._blades]

    @active_foils.setter
    def active_foils(self, active_foils: list):
        for i, blade in enumerate(self._blades):
            blade.active_foil = active_foils[i]

        # now reinitialize the filterset to get new list of filters and absorption table
        self._update_all()

    @property
    def index(self):
        filter_id = self.get_filter()
        return [f["position"] for f in self._built_filters].index(filter_id) + 1

    @index.setter
    def index(self, idx: int):
        if not (idx > 0 and idx < 17):
            raise ValueError("The filter index is out of range, expected [1 - 16]")
        self.set_filter(self._built_filters[idx - 1]["position"])

    def home(self):
        """Reset the position of the filter to the out position (for the current selection)"""
        for b in self._blades:
            b.home()

    def _encode(self, filters: list):
        filter_id = 0
        for i, f in enumerate(filters):
            if f is not None:
                filter_id += int(f + 1) << (4 * i)
        return filter_id

    def _decode(self, filter_id: int):
        filters = []
        for i in range(self.nb_blades):
            foil = filter_id >> (4 * i) & 0x0F
            if foil:
                filters.append(foil - 1)
            else:
                filters.append(None)
        return filters

    def _calc_transmissions(self, energy=None):
        """
        Calculate the transmission factors for the filters for the given energy
        """
        if energy is None:
            energy = self.energy_axis.position
        for blade in self._blades:
            blade._calc_transmissions(energy)
        # save in setting the last energy
        self._last_energy = energy

    # --------------------------------------------------------------
    # Here start the mother class overloaded methods to create
    # a new filterset
    # --------------------------------------------------------------

    def is_filter_enabled(self, filter_id):
        positions = [f["position"] for f in self._built_filters]
        if filter_id not in positions:
            raise ValueError(
                f"Wrong filter position {filter_id} supported values {positions}"
            )
        return filter_id in self.enabled_filters

    def can_enable_filters(self, enabled_filters=None):
        positions = [f["position"] for f in self._built_filters]
        print("enabled_filters", enabled_filters)
        for filter_id in enabled_filters:
            if filter_id not in positions:
                return False
        return True

    def set_filter(self, filter_id):
        """
        Set the new filter combinations, for a blade, it moves to the position set in config
        """
        filters = self._decode(filter_id)

        # Group move
        motions = [blade.set_filter(filters[i]) for i, blade in enumerate(self._blades)]
        _move({m[0]: m[1] for m in motions}, print_motion=False)

    def get_filter(self):
        """
        Return the current filter id.
        None is return if the axis position does not correspond to the
        defined positions
        """
        filters = [f.get_filter() for f in self._blades]
        return self._encode(filters)

    def get_transmission(self, filter_id=None):
        """
        Return the tranmission of filter filter_id
        if None, return the curent filter transmission
        """
        if not filter_id:
            filt = self.get_filter()
        else:
            filt = filter_id
        if filt is not None:
            for filter in self.get_filters():
                if filt == filter["position"]:
                    return filter["transmission_calc"]
            return -1
        else:
            return -1

    def build_filterset(self, enabled_filters=None):
        """
        Build pattern (index here)  and transmission arrays.
        A filterset, like Blade, is made of 4 filter blades (6 foils)
        which can be combined to produce 7^4 patterns and transmissions.
        """

        p = []
        t = []
        self._built_filters = []

        # List of all the possible values for each blade (either None or active foil)
        combinations = [[None, foil] for foil in self.active_foils]

        for filters in product(*combinations):
            filt_id = self._encode(filters)
            # store just the index of the filters as the possible pattern
            # if filt_id in enabled_filters:
            if True:
                transmissions = [
                    blade.get_transmission(filters[i])
                    for i, blade in enumerate(self._blades)
                    if filters[i] is not None
                ]
                trans = reduce(lambda x, y: x * y, transmissions, 1.0)

                p.append(filt_id)
                t.append(trans)

                self._built_filters.append(
                    {
                        "position": filt_id,
                        "filters": filters,
                        "transmission_calc": trans,
                    }
                )

        self._built_filters.sort(
            key=lambda filter: filter["transmission_calc"], reverse=True
        )

        self._fpattern = np.array(p, dtype=int)
        self._ftransm = np.array(t)

        return len(self._fpattern)

    def get_filters(self):
        """
        Return the list of the public filters, a list of dictionary items with at least:
        - position
        - transmission_calc
        For the wheel filterset _foils = _config_filters
        """
        return self._built_filters

    def scan_metadata(self):
        meta_dict = {"@NX_class": "NXattenuator"}
        meta_dict["position"] = self.position
        meta_dict["transmission"] = self.transmission
        meta_dict["active_foils"] = self.active_foils
        return meta_dict
