# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import os
import numpy
import tabulate

__all__ = [
    "copy_diffractometer_settings_from",
    "br",
    "ubr",
    "ca",
    "ca_",
    "ca_all",
    "ca_all_",
    "ci",
    "cior",
    "cior0",
    "cior1",
    "goto_or",
    "goto_or0",
    "goto_or1",
    "wh",
    "pa",
    "setmode",
    "setpsi",
    "freeze",
    "unfreeze",
    "pr_freeze",
    "setlat",
    "or0",
    "or1",
    "setor0",
    "setor1",
    "or_swap",
    "refadd",
    "refdel",
    "reflist",
    "refload",
    "refsave",
    "reffit",
    "setaz",
    "setnormal",
    "paUB",
    "showUB",
    "saveUB",
    "loadUB",
    "geolimits",
    "setgeolimits",
    "resetgeolimits",
    "aziscan",
    "azidscan",
    "psiscan",
    "psidscan",
    "hscan",
    "kscan",
    "lscan",
    "hklscan",
    "hdscan",
    "kdscan",
    "ldscan",
    "hkldscan",
    "hkcircle",
    "hkradial",
    "klcircle",
    "klradial",
    "hlcircle",
    "hlradial",
]

from bliss.controllers.diffractometers import get_current_diffractometer
from bliss.config.settings import HashObjSetting
from bliss.config.static import get_config
from bliss.common.cleanup import cleanup, axis as cleanup_axis
from bliss.common.standard import _move
from bliss.common.scans import ascan, dscan, lookupscan
from bliss.shell.getval import getval_float, getval_idx_list
from bliss.common.logtools import log_warning


def copy_diffractometer_settings_from(
    src_diffracto_name, target_diffracto=None, move_energy=False
):
    """
    Copy :
    - lattice
    - reflections
    - hkl mode
    - frozen angles
    - axis limits
    from diffractometer 'src_diffracto_name' to the current one, and move energy axis to the same value (if move_energy=true)
    """

    if target_diffracto is None:
        target_diffracto = get_current_diffractometer()

    src_geo_name = get_config().get_config(src_diffracto_name)["geometry"]
    trg_geo_name = target_diffracto.geometry_name

    if src_geo_name != trg_geo_name:
        raise RuntimeError(
            f"cannot copy settings from a diffractometer with a different geometry ({src_geo_name} != {trg_geo_name})"
        )

    src_settings = HashObjSetting(src_diffracto_name)

    src_energy = (
        target_diffracto.geometry.HC_OVER_E / src_settings["wavelength"]
    )  # Angstrom and keV
    try:
        trg_energy_axis = target_diffracto.get_axis("energy")
    except Exception:
        raise
    else:
        if trg_energy_axis.unit.lower() == "ev":
            energy_factor = 1000
        else:
            energy_factor = 1

        if move_energy:
            _move(
                {trg_energy_axis: src_energy * energy_factor},
                print_motion=True,
                display_dependencies=True,
            )
        else:
            print(
                f"INFO: {src_diffracto_name} energy is {src_energy:.4f}keV, {target_diffracto.name} energy is {trg_energy_axis.position / energy_factor:.4f}keV"
            )

    target_diffracto.sample.set_lattice(*src_settings["sample_lattice"])
    target_diffracto.sample.set_reflections(src_settings.get("sample_reflections"))
    if src_settings["sample_calc_mode"] == "manual":
        target_diffracto.sample.set_UB(src_settings["sample_UB"])
    else:
        target_diffracto.sample.computeUB()
    target_diffracto.geometry.set_mode("hkl", src_settings["hkl_mode"])
    target_diffracto._motor_calc.frozen_angles = src_settings["frozen_angles"]
    for k in src_settings.keys():
        if k.endswith("_limits"):
            axis_name = k.removesuffix("_limits")
            target_diffracto.get_axis(axis_name).limits = src_settings[k]
    target_diffracto.geo_limits = target_diffracto.motor_limits

    target_diffracto._calc_geo()


def br(h, k, l):  # noqa: E741
    diffracto = get_current_diffractometer()
    diffracto.move_hkl(h, k, l)


def ubr(h, k, l):  # noqa: E741
    diffracto = get_current_diffractometer()
    diffracto.umove_hkl(h, k, l)


def ca(h, k, l, all_solutions=False, use_extended_limits=False):  # noqa: E741
    diffracto = get_current_diffractometer()

    if use_extended_limits:
        current_axes_limits = diffracto.geometry.get_axis_limits()
        diffracto.geometry.set_axis_limits(diffracto.geometry.extended_limits)
    try:
        diffracto.check_hkl(h, k, l, all_solutions)
    finally:
        if use_extended_limits:
            diffracto.geometry.set_axis_limits(current_axes_limits)


def ca_all(h, k, l, use_extended_limits=False):  # noqa: E741
    """
    same as ca(h,k,l) with all_solutions set to True
    """
    ca(h, k, l, all_solutions=True, use_extended_limits=use_extended_limits)


def ca_(h, k, l, use_extended_limits=False):  # noqa: E741
    """
    calculate (h,k,l) positions and return (axis_pos, pseudo_pos) (2 dicts) for the closest solution (no prints)
    """
    diffracto = get_current_diffractometer()

    if use_extended_limits:
        current_axes_limits = diffracto.geometry.get_axis_limits()
        diffracto.geometry.set_axis_limits(diffracto.geometry.extended_limits)

    try:
        axis_pos, pseudo_pos = diffracto.compute_solution(h, k, l)
        return axis_pos, pseudo_pos
    except Exception as e:
        log_warning(diffracto, "%s", str(e))
        return ({}, {})
    finally:
        if use_extended_limits:
            diffracto.geometry.set_axis_limits(current_axes_limits)


def ca_all_(h, k, l, use_extended_limits=False):  # noqa: E741
    """
    calculate (h,k,l) positions and return a list of axis positions dict (no pseudos) for all the possible solutions (no prints)
    """
    diffracto = get_current_diffractometer()
    all_calc_pos = []

    if use_extended_limits:
        current_axes_limits = diffracto.geometry.get_axis_limits()
        diffracto.geometry.set_axis_limits(diffracto.geometry.extended_limits)

    try:
        diffracto.compute_solution(h, k, l, all_solutions=all_calc_pos)
    except Exception as e:
        log_warning(diffracto, "%s", str(e))
    finally:
        if use_extended_limits:
            diffracto.geometry.set_axis_limits(current_axes_limits)

    return all_calc_pos


def ci(*angles):
    diffracto = get_current_diffractometer()
    axis_names = diffracto.geometry.get_axis_names()
    pos_dict = dict(list(zip(axis_names, angles)))
    diffracto.check_pos(pos_dict)


def cior(idx):
    """
    do an angles to pseudos calculation using the positions of the reflection #idx
    """
    diffracto = get_current_diffractometer()
    (h, k, l), pos_dict, _ = diffracto.sample.get_one_reflection(idx)
    print(f"Using positions of reference {idx} at ({h:.5f}, {k:.5f}, {l:.5f})")
    diffracto.check_pos(pos_dict)


def cior0():
    """
    do an angles to pseudos calculation using the positions of the primary reflection
    """
    cior(0)


def cior1():
    """
    do an angles to pseudos calculation using the positions of the secondary reflection
    """
    cior(1)


def goto_or(idx, print_motion=True, display_dependencies=True):
    """
    move the diffractomenter motors to the positions of the reflection #idx
    """
    diffracto = get_current_diffractometer()
    _, pos_dict, _ = diffracto.sample.get_one_reflection(idx)
    _move(
        {diffracto.get_axis(tag): pos for tag, pos in pos_dict.items()},
        print_motion=print_motion,
        display_dependencies=display_dependencies,
    )


def goto_or0():
    """
    move the diffractomenter motors to the positions of the primary reflection
    """
    goto_or(0)


def goto_or1():
    """
    move the diffractomenter motors to the positions of the secondary reflection
    """
    goto_or(1)


def wh():
    diffracto = get_current_diffractometer()
    diffracto.show_pos()


def pa():
    diffracto = get_current_diffractometer()
    diffracto.show()


def freeze(*vals):
    diffracto = get_current_diffractometer()
    diffracto.freeze(*vals)


def unfreeze():
    diffracto = get_current_diffractometer()
    diffracto.unfreeze()


def pr_freeze():
    diffracto = get_current_diffractometer()
    diffracto.pr_freeze()


def setmode(modename=None):
    diffracto = get_current_diffractometer()
    mode_list = diffracto.hklmode_list
    curr_mode = diffracto.hklmode
    if modename is None:
        defval = mode_list.index(curr_mode) + 1
        idx, _ = getval_idx_list(
            mode_list, message="Enter mode index: ", default=defval
        )
        diffracto.hklmode = mode_list[idx - 1]
    elif isinstance(modename, int):
        if modename < 1:
            raise ValueError("mode index should be > 0")
        diffracto.hklmode = mode_list[modename - 1]
    else:
        if modename not in mode_list:
            raise ValueError(f"invalide mode name, should be in {mode_list}")
        diffracto.hklmode = modename

    new_mode = diffracto.hklmode
    if curr_mode != new_mode:
        print("Switching to HKL mode [{0}]".format(new_mode))
        if len(diffracto.frozen_angles_names):
            print("Use freeze() to fix constant angles.")
    else:
        print("Still using HKL mode [{0}]".format(curr_mode))


def setpsi(psi):
    diffracto = get_current_diffractometer()
    if hasattr(diffracto, "psi_constant"):
        diffracto.psi_constant = psi
    else:
        raise ValueError("Current diffractometer does not have psi_constant mode")


def or0(*hkl_values):  # noqa: E741
    diffracto = get_current_diffractometer()
    try:
        vals_dict = dict(zip(("h", "k", "l"), diffracto.or0[0:3]))
    except ValueError:
        vals_dict = dict(zip(("h", "k", "l"), (None,) * 3))

    if len(hkl_values) == 3:
        diffracto.or0 = tuple(map(float, hkl_values))
    else:
        print("Enter hkl values:")
        for key, value in vals_dict.items():
            vals_dict[key] = getval_float(f" {key}", default=value)
        diffracto.or0 = tuple(vals_dict.values())


def or1(*hkl_values):  # noqa: E741
    diffracto = get_current_diffractometer()
    try:
        vals_dict = dict(zip(("h", "k", "l"), diffracto.or1[0:3]))
    except ValueError:
        vals_dict = dict(zip(("h", "k", "l"), (None,) * 3))

    if len(hkl_values) == 3:
        diffracto.or1 = tuple(map(float, hkl_values))
    else:
        print("Enter hkl values:")
        for key, value in vals_dict.items():
            vals_dict[key] = getval_float(f" {key}", default=value)
        diffracto.or1 = tuple(vals_dict.values())


def setor0(*vals):
    diffracto = get_current_diffractometer()
    if len(vals) != (3 + len(diffracto.axis_names)):
        vals = ask_or_values(0, diffracto)
    diffracto.or0 = vals


def setor1(*vals):
    diffracto = get_current_diffractometer()
    if len(vals) != (3 + len(diffracto.axis_names)):
        vals = ask_or_values(1, diffracto)
    diffracto.or1 = vals


def ask_or_values(oridx, diffobj):

    try:
        vals_dict = dict(zip(("h", "k", "l"), diffobj.reflist[oridx][0:3]))
    except IndexError:
        vals_dict = dict(zip(("h", "k", "l"), (None,) * 3))

    if oridx == 0:
        refstr = "primary-reflection"
    elif oridx == 1:
        refstr = "secondary-reflection"
    else:
        refstr = "reflection"

    print("Enter {0} HKL coordinates:".format(refstr))
    for key, value in vals_dict.items():
        vals_dict[key] = getval_float(f" {key}", default=value)

    try:
        vals_dict.update(dict(zip(diffobj.axis_names, diffobj.reflist[oridx][3:])))
    except IndexError:
        vals_dict.update(
            dict(zip(diffobj.axis_names, (None,) * len(diffobj.axis_names)))
        )

    print("Enter {0} angles:".format(refstr))
    for name in diffobj._reals_names:
        vals_dict[name] = getval_float(
            f" {diffobj.motor_names[name]}", default=vals_dict[name]
        )

    return tuple(vals_dict.values())


def or_swap():
    diffracto = get_current_diffractometer()
    diffracto.or_swap()


def refadd(*vals):
    diffracto = get_current_diffractometer()
    if len(vals) == 3:
        diffracto.refadd(*vals)
    elif len(vals) == (3 + len(diffracto.axis_names)):
        diffracto.refadd(*vals)
    else:
        vals = ask_or_values(2, diffracto)
        diffracto.refadd(*vals)


def refdel(*index):
    diffracto = get_current_diffractometer()
    diffracto.refdel(*index)


def reflist():
    diffracto = get_current_diffractometer()
    _reflist = diffracto.reflist
    refout = list()
    for (idx, ref) in zip(range(len(_reflist)), _reflist):
        refout.append(("[{0}]".format(idx),) + ref)
    print(tabulate.tabulate(refout, ("index",) + diffracto.refhead, "simple"))


def refsave(filename):
    diffracto = get_current_diffractometer()
    diffracto.refsave(filename)


def refload(filename):
    diffracto = get_current_diffractometer()
    diffracto.refload(filename)


def reffit():
    diffracto = get_current_diffractometer()
    diffracto.reffit()


def setlat(*vals):
    diffracto = get_current_diffractometer()
    if len(vals) == 6:
        diffracto.lattice = tuple(map(float, vals))
    else:
        print("Enter real space lattice parameters:")
        vals_dict = dict(
            zip(("a", "b", "c", "alpha", "beta", "gamma"), diffracto.lattice)
        )
        for key, value in vals_dict.items():
            vals_dict[key] = getval_float(f" Lattice {key}", default=value)
        diffracto.lattice = tuple(vals_dict.values())


def setaz(h, k, l):  # noqa: E741
    diffracto = get_current_diffractometer()
    if hasattr(diffracto, "azimuth_ref"):
        diffracto.azimuth_ref = (h, k, l)
    else:
        raise ValueError(
            "Diffractometer [{0}] does not have azimuth reference".format(
                diffracto.name
            )
        )


def setnormal(h, k, l):  # noqa: E741
    diffracto = get_current_diffractometer()
    if hasattr(diffracto, "normal_ref"):
        diffracto.normal_ref = (h, k, l)
    else:
        raise ValueError(
            "Diffractometer [{0}] does not have normal reference".format(diffracto.name)
        )


def paUB():
    diffracto = get_current_diffractometer()
    diffracto.show_ref()


def showUB():
    diffracto = get_current_diffractometer()
    UB = diffracto.UB
    print("Orientation matrix:")
    print(UB)


def saveUB(filename):
    """
    save UB matrix, lattice parameters and references to a txt file
    """
    diffracto = get_current_diffractometer()
    with open(filename, "w") as reffile:
        reffile.write("# UB MATRIX\n")
        reffile.write(tabulate.tabulate(diffracto.sample.get_UB(), "", "plain") + "\n")
        reffile.write("# LATTICE PARAMETERS\n")
        reffile.write(
            "{0:.5f} {1:.5f} {2:.5f} {3:.5f} {4:.5f} {5:.5f}\n".format(
                *diffracto.sample.get_lattice()
            )
        )
        reffile.write("# REFERENCES\n")
        refs = list()
        for (hkl, pos, wl) in diffracto.sample.get_reflections():
            refs.append(hkl + tuple(pos.values()) + tuple([wl]))
        refhead = ("H", "K", "L") + tuple(pos.keys()) + tuple(["wavelength"])
        reffile.write("#" + tabulate.tabulate(refs, refhead, "plain") + "\n")
        print(f"### matrix saved to {os.path.realpath(reffile.name)}")


def loadUB(filename):
    """
    load UB matrix, lattice parameters and references from a txt file
    """
    diffracto = get_current_diffractometer()
    with open(filename, "r") as reffile:
        reffile.readline()  # UB MATRIX\n
        UB = numpy.array(
            [tuple(map(float, reffile.readline().split())) for i in range(3)]
        )
        reffile.readline()  # LATTICE PARAMETERS\n
        lattice = tuple(map(float, reffile.readline().split()))
        reffile.readline()  # REFERENCES\n
        reffile.readline()  # refhead
        ref_list = list()
        while (line := reffile.readline()) != "":
            ref_list.append(tuple(map(float, line.split())))
    diffracto.sample.set_lattice(*lattice)
    for i, ref in enumerate(ref_list):
        diffracto.sample.set_one_reflection(
            i, ref[0:3], dict(zip(diffracto.axis_names, ref[3:-1])), ref[-1]
        )
    diffracto._calc_geo()
    return UB, lattice, tuple(ref_list)


def geolimits():
    diffracto = get_current_diffractometer()
    mot_lim = diffracto.motor_limits
    geo_lim = diffracto.geo_limits
    ext_lim = diffracto.extended_limits
    all_lim = list()
    print("\nCurrent motor and geometry limits:")
    for name in geo_lim.keys():
        all_lim.append(
            [
                name,
                mot_lim[name][0],
                mot_lim[name][1],
                geo_lim[name][0],
                geo_lim[name][1],
                ext_lim[name][0],
                ext_lim[name][1],
            ]
        )
    all_head = (
        "name",
        "mot[lim-]",
        "mot[lim+]",
        "geo[lim-]",
        "geo[lim+]",
        "ext[lim-]",
        "ext[lim+]",
    )
    print(tabulate.tabulate(all_lim, all_head, "simple"))
    print()


def setgeolimits():
    diffracto = get_current_diffractometer()
    mot_lim = diffracto.motor_limits
    geo_lim = diffracto.geo_limits
    for name in geo_lim.keys():
        print("{0} motor limits are {1}:".format(name, mot_lim[name]))
        val0 = getval_float(
            f"Enter {name} geometry negative limit:", default=geo_lim[name][0]
        )
        val1 = getval_float(
            f"Enter {name} geometry negative limit:", default=geo_lim[name][1]
        )

        if len(val0):
            geo_lim[name] = (float(val0), geo_lim[name][1])

        if len(val1):
            geo_lim[name] = (geo_lim[name][0], float(val1))
    diffracto.geo_limits = geo_lim
    geolimits()


def resetgeolimits():
    diffracto = get_current_diffractometer()
    diffracto.geo_limits = diffracto.motor_limits
    geolimits()


def _one_pseudo_scan(
    scan_name, motor_name, val1, val2, intervals, count_time, *counter_args, **kwargs
):
    diffracto = get_current_diffractometer()
    if motor_name not in diffracto.pseudo_names:
        raise RuntimeError(
            "Current diffractometer [{0}] does not have pseudo type [{1}]".format(
                diffracto.name, motor_name
            )
        )

    diffmotor = diffracto.get_axis(motor_name)
    title = "{0} {1} {2} {3} {4}".format(scan_name, val1, val2, intervals, count_time)
    kwargs.update({"type": scan_name, "title": title})
    ascan(diffmotor, val1, val2, intervals, count_time, *counter_args, **kwargs)


def _one_pseudo_dscan(
    scan_name, motor_name, val1, val2, intervals, count_time, *counter_args, **kwargs
):
    diffracto = get_current_diffractometer()
    if motor_name not in diffracto.pseudo_names:
        raise RuntimeError(
            "Current diffractometer [{0}] does not have pseudo type [{1}]".format(
                diffracto.name, motor_name
            )
        )
    diffmotor = diffracto.get_axis(motor_name)
    title = "{0} {1} {2} {3} {4}".format(scan_name, val1, val2, intervals, count_time)
    kwargs.update({"type": scan_name, "title": title})
    dscan(diffmotor, val1, val2, intervals, count_time, *counter_args, **kwargs)


def aziscan(az1, az2, intervals, count_time, *counter_args, **kwargs):
    _one_pseudo_scan(
        "aziscan", "psi_psi", az1, az2, intervals, count_time, *counter_args, **kwargs
    )


psiscan = aziscan


def azidscan(daz1, daz2, intervals, count_time, *counter_args, **kwargs):
    _one_pseudo_dscan(
        "azidscan",
        "psi_psi",
        daz1,
        daz2,
        intervals,
        count_time,
        *counter_args,
        **kwargs,
    )


psidscan = azidscan


def hscan(h1, h2, intervals, count_time, *counter_args, **kwargs):
    diffracto = get_current_diffractometer()
    (h, k, l) = diffracto.hkl
    hklscan((h1, k, l), (h2, k, l), intervals, count_time, *counter_args, **kwargs)


def kscan(k1, k2, intervals, count_time, *counter_args, **kwargs):
    diffracto = get_current_diffractometer()
    (h, k, l) = diffracto.hkl
    hklscan((h, k1, l), (h, k2, l), intervals, count_time, *counter_args, **kwargs)


def lscan(l1, l2, intervals, count_time, *counter_args, **kwargs):
    diffracto = get_current_diffractometer()
    (h, k, l) = diffracto.hkl
    hklscan((h, k, l1), (h, k, l2), intervals, count_time, *counter_args, **kwargs)


def hklscan(hkl1, hkl2, intervals, count_time, *counter_args, **kwargs):
    """
    HKL scans
    """

    diffracto = get_current_diffractometer()
    (h1, k1, l1) = hkl1
    (h2, k2, l2) = hkl2

    npoints = intervals + 1
    h_pos = numpy.linspace(h1, h2, npoints)
    k_pos = numpy.linspace(k1, k2, npoints)
    l_pos = numpy.linspace(l1, l2, npoints)

    h_motor = diffracto.get_axis("hkl_h")
    k_motor = diffracto.get_axis("hkl_k")
    l_motor = diffracto.get_axis("hkl_l")

    motpos_args = [(h_motor, h_pos), (k_motor, k_pos), (l_motor, l_pos)]

    kwargs.setdefault("scan_type", "hklscan")
    kwargs.setdefault("name", "hklscan")
    kwargs.setdefault(
        "title",
        "hklscan {0} {1} {2} {3}".format(
            tuple(round(x, 3) for x in hkl1),
            tuple(round(x, 3) for x in hkl2),
            intervals,
            count_time,
        ),
    )
    kwargs.setdefault("scan_info", {"start": [h1, k1, l1], "stop": [h2, k2, l2]})

    return lookupscan(motpos_args, count_time, *counter_args, **kwargs)


def hdscan(dh1, dh2, intervals, count_time, *counter_args, **kwargs):
    hkldscan((dh1, 0, 0), (dh2, 0, 0), intervals, count_time, *counter_args, **kwargs)


def kdscan(dk1, dk2, intervals, count_time, *counter_args, **kwargs):
    hkldscan((0, dk1, 0), (0, dk2, 0), intervals, count_time, *counter_args, **kwargs)


def ldscan(dl1, dl2, intervals, count_time, *counter_args, **kwargs):
    hkldscan((0, 0, dl1), (0, 0, dl2), intervals, count_time, *counter_args, **kwargs)


def hkldscan(dhkl1, dhkl2, intervals, count_time, *counter_args, **kwargs):
    diffracto = get_current_diffractometer()
    (dh1, dk1, dl1) = dhkl1
    (dh2, dk2, dl2) = dhkl2
    (horg, korg, lorg) = diffracto.hkl

    npoints = intervals + 1
    h_pos = numpy.linspace(horg + dh1, horg + dh2, npoints)
    k_pos = numpy.linspace(korg + dk1, korg + dk2, npoints)
    l_pos = numpy.linspace(lorg + dl1, lorg + dl2, npoints)

    h_motor = diffracto.get_axis("hkl_h")
    k_motor = diffracto.get_axis("hkl_k")
    l_motor = diffracto.get_axis("hkl_l")

    motpos_args = [(h_motor, h_pos), (k_motor, k_pos), (l_motor, l_pos)]

    kwargs.setdefault("scan_type", "hkldscan")
    kwargs.setdefault("name", "hkldscan")
    kwargs.setdefault(
        "title",
        "hkldscan {0} {1} {2} {3}".format(
            tuple(round(x, 3) for x in dhkl1),
            tuple(round(x, 3) for x in dhkl2),
            intervals,
            count_time,
        ),
    )
    kwargs.setdefault("scan_info", {"start": [dh1, dk1, dl1], "stop": [dh2, dk2, dl2]})

    with cleanup(
        h_motor, k_motor, l_motor, restore_list=(cleanup_axis.POS,), verbose=True
    ):
        scan = lookupscan(motpos_args, count_time, *counter_args, **kwargs)

    return scan


def hkcircle(radius, start, stop, intervals, count_time, *counter_args, **kwargs):
    motpos_args = _calc_hkl_circle(
        "hkl_h", "hkl_k", radius, start, stop, intervals, **kwargs
    )
    motpos_args += counter_args
    return _do_hkl_line_scan(
        "hkcircle", radius, start, stop, intervals, count_time, *motpos_args, **kwargs
    )


def klcircle(radius, start, stop, intervals, count_time, *counter_args, **kwargs):
    motpos_args = _calc_hkl_circle(
        "hkl_k", "hkl_l", radius, start, stop, intervals, **kwargs
    )
    motpos_args += counter_args
    return _do_hkl_line_scan(
        "klcircle", radius, start, stop, intervals, count_time, *motpos_args, **kwargs
    )


def hlcircle(radius, start, stop, intervals, count_time, *counter_args, **kwargs):
    motpos_args = _calc_hkl_circle(
        "hkl_h", "hkl_l", radius, start, stop, intervals, **kwargs
    )
    motpos_args += counter_args
    return _do_hkl_line_scan(
        "hlcircle", radius, start, stop, intervals, count_time, *motpos_args, **kwargs
    )


def hkradial(angle, start, stop, intervals, count_time, *counter_args, **kwargs):
    motpos_args = _calc_hkl_radial(
        "hkl_h", "hkl_k", angle, start, stop, intervals, **kwargs
    )
    motpos_args += counter_args
    return _do_hkl_line_scan(
        "hkradial", angle, start, stop, intervals, count_time, *motpos_args, **kwargs
    )


def klradial(angle, start, stop, intervals, count_time, *counter_args, **kwargs):
    motpos_args = _calc_hkl_radial(
        "hkl_k", "hkl_l", angle, start, stop, intervals, **kwargs
    )
    motpos_args += counter_args
    return _do_hkl_line_scan(
        "klradial", angle, start, stop, intervals, count_time, *motpos_args, **kwargs
    )


def hlradial(angle, start, stop, intervals, count_time, *counter_args, **kwargs):
    motpos_args = _calc_hkl_radial(
        "hkl_h", "hkl_l", angle, start, stop, intervals, **kwargs
    )
    motpos_args += counter_args
    return _do_hkl_line_scan(
        "hlradial", angle, start, stop, intervals, count_time, *motpos_args, **kwargs
    )


def _calc_hkl_circle(
    axis1, axis2, radius, angle_start, angle_stop, intervals, **kwargs
):
    diffracto = get_current_diffractometer()
    npoints = intervals + 1
    steps = numpy.linspace(angle_start, angle_stop, npoints)
    pos1 = radius * numpy.sin(numpy.radians(steps))
    pos2 = radius * numpy.cos(numpy.radians(steps))

    motpos = list()
    motpos.extend((diffracto.get_axis(axis1), pos1))
    motpos.extend((diffracto.get_axis(axis2), pos2))
    return motpos


def _calc_hkl_radial(axis1, axis2, angle, start, stop, intervals, **kwargs):
    diffracto = get_current_diffractometer()
    npoints = intervals + 1
    steps = numpy.linspace(start, stop, npoints)
    pos1 = steps * numpy.sin(numpy.radians(angle))
    pos2 = steps * numpy.cos(numpy.radians(angle))

    motpos = list()
    motpos.extend((diffracto.get_axis(axis1), pos1))
    motpos.extend((diffracto.get_axis(axis2), pos2))
    return motpos


def _do_hkl_line_scan(
    name,
    value,
    start,
    stop,
    intervals,
    count_time,
    motpos_args,
    *counter_args,
    **kwargs,
):
    kwargs.setdefault("type", name)
    kwargs.setdefault("name", name)
    kwargs.setdefault(
        "title",
        "{0} {1} {2} {3} {4} {5}".format(
            name, value, start, stop, intervals, count_time
        ),
    )
    return lookupscan(motpos_args, count_time, *counter_args, **kwargs)
