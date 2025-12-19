# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from tabulate import tabulate
from bliss.shell.getval import getval_float
from .diff_base import Diffractometer


class DiffE6C(Diffractometer):
    def show(self):
        # Geometry
        txt = f"\nGeometry: {self.geometry_name}\n"

        # HKL mode and params
        txt += f"\n{self._get_hklpars()}\n"

        # Frozen angles
        if self.frozen_angles_names:
            head = [f"{self._motor_names[k]} [{k}]" for k in self.frozen_angles_names]
            lines = [[self.frozen_angles.get(k) for k in self.frozen_angles_names]]
            tab = tabulate(
                lines,
                head,
                floatfmt=".4f",
                missingval="None",
                tablefmt="rounded_outline",
            )
            txt += f"\nFrozen angles:\n{tab}\n"

        # Reflections
        numofref = self.sample.get_n_reflections()
        if numofref == 0:
            txt += "\nReflections not yet defined\n"
        else:
            head = ["Index", "Lambda", "HKL"] + [k for k in self._reals_names]
            lines = []
            for refnum in range(0, numofref):
                (hkl, pos, wl) = self.sample.get_one_reflection(refnum)
                lines.append(
                    [f"#{refnum}", f"{wl:.4f}", f"{hkl[0]} {hkl[1]} {hkl[2]}"]
                    + [pos[k] for k in self._reals_names]
                )
            tab = tabulate(lines, head, floatfmt=".4f", tablefmt="rounded_outline")
            txt += f"\nReflections:\n{tab}\n"

        # Lattice
        lines = [
            ["real"] + list(self.sample.get_lattice()),
            ["reciprocal"] + list(self.sample.get_reciprocal_lattice()),
        ]
        tab = tabulate(
            lines, floatfmt=".4f", missingval="None", tablefmt="rounded_outline"
        )
        txt += f"\nLattice parameters (lengths / angles):\n{tab}\n"

        # Energy
        txt += f"\nLambda = {self.wavelength:.5f}  Energy = {self.energy:.3f} keV\n"

        print(txt)

    @property
    def hklpars(self):
        print(self._get_hklpars())

    def _get_hklpars(self):
        current_mode = self.hklmode
        txt = f"HKL mode: {current_mode}"
        pars_dict = self.geometry.get_mode_pars("hkl", current_mode)
        if pars_dict:
            head = list(pars_dict.keys())
            lines = [list(pars_dict.values())]
            tab = tabulate(lines, head, floatfmt=".4f", tablefmt="rounded_outline")
            txt += f"\n{tab}"
        return txt

    def set_hklpars(self):
        current_mode = self.hklmode
        pars_dict = self.geometry.get_mode_pars("hkl", current_mode)
        for key in pars_dict.keys():
            oldval = pars_dict[key]
            newval = getval_float(f"{key}", default=oldval)
            if newval:
                pars_dict[key] = float(newval)
        self.geometry.set_mode_pars("hkl", current_mode, pars_dict)
