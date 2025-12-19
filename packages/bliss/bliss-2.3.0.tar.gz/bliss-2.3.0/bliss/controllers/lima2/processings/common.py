# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from typing import Literal

from bliss import current_session

from bliss.common.utils import typecheck
import bliss.common.plot as plot_module  # for edit_rois

from bliss.shell.formatters.table import IncrementalTable

from bliss.controllers.lima.roi import Roi, ArcRoi, RoiProfile

from bliss.controllers.lima2.tabulate import tabulate
from bliss.controllers.lima2.settings import Settings, setting_property
from bliss.controllers.lima2.counter import RoiStatCounters, RoiProfCounters
from bliss.controllers.lima2.controller import RoiStatController, RoiProfilesController


class Saving(Settings):
    def __init__(self, config, path, params, title=""):
        self._params = params
        self._title = title
        super().__init__(config, path)

    @setting_property(default=True)
    def enabled(self):
        return self._params["enabled"]

    @enabled.setter
    @typecheck
    def enabled(self, value: bool):
        self._params["enabled"] = value

    @setting_property(default="bshuf_lz4")
    def compression(self):
        return self._params["compression"]

    @compression.setter
    @typecheck
    def compression(self, value: str):
        self._params["compression"] = value

    @setting_property(default=50)
    def nb_frames_per_file(self):
        return self._params["nb_frames_per_file"]

    @nb_frames_per_file.setter
    @typecheck
    def nb_frames_per_file(self, value: int):
        self._params["nb_frames_per_file"] = value

    @setting_property(default="abort")
    def file_exists_policy(self):
        return self._params["file_exists_policy"]

    @file_exists_policy.setter
    @typecheck
    def file_exists_policy(self, value: str):
        self._params["file_exists_policy"] = value

    @setting_property(default="dim_3d_or_4d")
    def nb_dimensions(self):
        return self._params["nb_dimensions"]

    @nb_dimensions.setter
    @typecheck
    def nb_dimensions(self, value: str):
        self._params["nb_dimensions"] = value

    def __info__(self):
        header = "Saving%s\n" % (f" {self._title}" if self._title else "")
        return header + tabulate(self._params)


class RoiStatistics(Settings):
    def __init__(self, config, path, params):
        self._params = params
        self._rois: list[Roi | ArcRoi] = []
        super().__init__(config, path)

    @setting_property
    def rois(self) -> list:
        return self._rois

    @rois.setter
    @typecheck
    def rois(self, values: list[Roi | ArcRoi]):
        # Check for uniqueness of the ROI names
        names = [roi.name for roi in values]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        if duplicates:
            raise ValueError(
                f"Found rois with duplicate names: {duplicates}. "
                "Please use different names for each roi."
            )

        self._rois = values

        self._params["rect_rois"] = [
            {
                "topleft": {"x": roi.x, "y": roi.y},
                "dimensions": {"x": roi.width, "y": roi.height},
            }
            for roi in values
            if type(roi) is Roi
        ]

        self._params["arc_rois"] = [
            {
                "center": {"x": roi.cx, "y": roi.cy},
                "r1": roi.r1,
                "r2": roi.r2,
                "a1": roi.a1,
                "a2": roi.a2,
            }
            for roi in values
            if type(roi) is ArcRoi
        ]

    def _add_roi(self, roi: Roi | ArcRoi):
        """Add a roi. If a roi with the same name exists, overwrite it."""
        self.rois = [r for r in self._rois if r.name != roi.name] + [roi]

    def _remove_roi(self, name: str):
        names = [roi.name for roi in self._rois]
        if name not in names:
            raise ValueError(f"No roi with name '{name}'")

        self.rois = [roi for roi in self._rois if roi.name != name]

    def _get_roi(self, name: str):
        matches = [roi for roi in self._rois if roi.name == name]

        if not matches:
            raise ValueError(f"No roi with name '{name}'")

        return matches[0]

    # dict like API
    @typecheck
    def set_rect(self, name: str, x: int, y: int, width: int, height: int):
        """Add/modify a rectangular roi in which to compute statistics over all pixels."""
        self._add_roi(Roi(x=x, y=y, width=width, height=height, name=name))

    @typecheck
    def set_arc(
        self,
        name: str,
        cx: int | float,
        cy: int | float,
        r1: int | float,
        r2: int | float,
        a1: int | float,
        a2: int | float,
    ):
        """Add/modify an arc roi in which to compute statistics over all pixels.

        Args:
          cx: center x
          cy: center y
          r1: inner radius
          r2: outer radius
          a1: start angle (degrees, from vertical)
          a2: end angle (degrees, from vertical)
        """
        self._add_roi(
            ArcRoi(
                cx=float(cx),
                cy=float(cy),
                r1=float(r1),
                r2=float(r2),
                a1=float(a1),
                a2=float(a2),
                name=name,
            )
        )

    def get(self, name: str) -> Roi | ArcRoi:
        return self._get_roi(name)

    def __getitem__(self, name: str) -> Roi | ArcRoi:
        return self._get_roi(name)

    @typecheck
    def __setitem__(self, name: str, roi: Roi | ArcRoi):
        roi._name = name
        self._add_roi(roi)

    # @typecheck
    def __delitem__(self, name: str):
        self._remove_roi(name)

    def __info__(self):
        header = "ROI Statistics\n"
        if self._rois:
            labels = ["Name", "Parameters", "State"]
            tab = IncrementalTable([labels])

            for roi in self._rois:
                tab.add_line(
                    [
                        roi.name,
                        str(roi),
                        "Enabled" if self._params["enabled"] else "Disabled",
                    ]
                )

            tab.resize(minwidth=10, maxwidth=100)
            tab.add_separator(sep="-", line_index=1)
            return header + str(tab) + "\n"
        else:
            return header + "*** no ROIs defined ***" + "\n"


class RoiProfiles(Settings):
    def __init__(self, config, path, params):
        self._params = params
        self._rois = []
        super().__init__(config, path)

    @setting_property
    def rois(self) -> list:
        return self._rois

    @rois.setter
    @typecheck
    def rois(self, values: list[RoiProfile]):
        # Check for uniqueness of the ROI names
        names = [roi.name for roi in values]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        if duplicates:
            raise ValueError(
                f"Found roi profiles with duplicate names: {duplicates}. "
                "Please use different names for each profile."
            )

        self._rois = values

        self._params["rois"] = [
            {
                "topleft": {"x": roi.x, "y": roi.y},
                "dimensions": {"x": roi.width, "y": roi.height},
            }
            for roi in values
        ]

        self._params["directions"] = [roi.mode for roi in values]

    def _add_profile(self, profile: RoiProfile):
        """Add a roi profile. If a profile with the same name exists, overwrite it."""
        self.rois = [r for r in self._rois if r.name != profile.name] + [profile]

    def _remove_profile(self, name: str):
        names = [roi.name for roi in self._rois]
        if name not in names:
            raise ValueError(f"No profile with name '{name}'")

        self.rois = [roi for roi in self._rois if roi.name != name]

    def _get_profile(self, name: str):
        matches = [roi for roi in self._rois if roi.name == name]

        if not matches:
            raise ValueError(f"No profile with name '{name}'")

        return matches[0]

    @typecheck
    def __setitem__(self, name: str, profile: RoiProfile):
        profile._name = name
        self._add_profile(profile=profile)

    # dict like API
    @typecheck
    def set(
        self,
        name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        mode: Literal["horizontal", "vertical"],
    ):
        """Add/modify a rectangular roi in which to compute a statistics profile."""
        self._add_profile(
            profile=RoiProfile(
                x=x, y=y, width=width, height=height, mode=mode, name=name
            )
        )

    # @typecheck
    def get(self, name: str) -> RoiProfile:
        return self._get_profile(name)

    # @typecheck
    def __getitem__(self, name: str) -> RoiProfile:
        return self._get_profile(name)

    # @typecheck
    def __delitem__(self, name: str):
        self._remove_profile(name)

    def __info__(self):
        header = "ROI Profiles\n"
        if self._rois:
            labels = ["Name", "Parameters", "State"]
            tab = IncrementalTable([labels])

            for roi in self._rois:
                tab.add_line(
                    [
                        roi.name,
                        str(roi),
                        "Enabled" if self._params["enabled"] else "Disabled",
                    ]
                )

            tab.resize(minwidth=10, maxwidth=100)
            tab.add_separator(sep="-", line_index=1)
            return header + str(tab) + "\n"
        else:
            return header + "*** no ROIs defined ***" + "\n"


class HasRoi:
    def _init_with_device(self, device):
        self._roi_counters_cc = RoiStatController(
            roi_stats=self.roi_stats,
            pipeline=device._lima2.pipeline,
            master_controller=device._frame_cc,
        )

        self._roi_profiles_cc = RoiProfilesController(
            roi_profiles=self.roi_profiles,
            pipeline=device._lima2.pipeline,
            master_controller=device._frame_cc,
        )

    def _get_roi_counters(self):
        res = []

        if self.use_roi_stats:
            rois = self.roi_stats.rois
            for roi in rois:
                res.extend(RoiStatCounters(roi, self._roi_counters_cc))
            self._roi_counters_cc._rois = rois
        if self.use_roi_profiles:
            rois = self.roi_profiles.rois
            for roi in rois:
                res.extend(RoiProfCounters(roi, self._roi_profiles_cc))
            self._roi_profiles_cc._rois = rois

        return res

    def edit_rois(self):
        """
        Edit this detector ROI counters with Flint.

        When called without arguments, it will use the image from specified detector
        from the last scan/ct as a reference. If `acq_time` is specified,
        it will do a `ct()` with the given count time to acquire a new image.

        .. code-block:: python

            # Flint will be open if it is not yet the case
            pilatus1.edit_rois(0.1)

            # Flint must already be open
            ct(0.1, pilatus1)
            pilatus1.edit_rois()
        """
        # Check that Flint is already there
        flint = plot_module.get_flint()

        # def update_image_in_plot():
        #     """Create a single frame from detector data if available
        #     else use a placeholder.
        #     """
        #     try:
        #         image_data = image_utils.image_from_server(self._proxy, -1)
        #         data = image_data.array
        #     except Exception:
        #         # Else create a checker board place holder
        #         y, x = np.mgrid[0 : self.image.height, 0 : self.image.width]
        #         data = ((y // 16 + x // 16) % 2).astype(np.uint8) + 2
        #         data[0, 0] = 0
        #         data[-1, -1] = 5

        #     channel_name = f"{self.name}:frame"
        #     flint.set_static_image(channel_name, data)

        # That it contains an image displayed for this detector
        det_name = self._device.name
        plot_name = det_name
        try:
            current_mg = current_session.env_dict["ACTIVE_MG"]
            if f"{det_name}:frame" not in current_mg.enabled:

                def is_frame(x):
                    return x.startswith(det_name) and x.endswith("_frame")

                plot_names = [x for x in current_mg.enabled if is_frame(x)]
                plot_name = plot_names[0] if plot_names else det_name
        except Exception:
            pass
        plot_proxy = flint.get_live_plot(image_detector=plot_name)
        ranges = plot_proxy.get_data_range()
        if ranges[0] is None:
            # update_image_in_plot()
            pass
        plot_proxy.focus()

        # Retrieve all the ROIs
        selection = []
        selection.extend(self.roi_stats.rois)
        selection.extend(self.roi_profiles.rois)

        print(f"Waiting for ROI edition to finish on {det_name}...")
        selection = plot_proxy.select_shapes(
            selection,
            kinds=[
                "lima-rectangle",
                "lima-arc",
                "lima-vertical-profile",
                "lima-horizontal-profile",
            ],
        )

        self.roi_stats.rois = [roi for roi in selection if type(roi) in (Roi, ArcRoi)]
        self.roi_profiles.rois = [roi for roi in selection if type(roi) is RoiProfile]

        roi_string = ", ".join(sorted([s.__repr__() for s in selection]))
        print(f"Applied ROIS {roi_string} to {det_name}")


class MaxCountrateProtection(Settings):
    def __init__(self, config, path, params):
        self._params = params
        config_info = config.get("max_countrate_protection", {})
        self._full_cmd = config_info.get("full_command", "") if config_info else ""
        if self._full_cmd:
            args = self._full_cmd.split()
            cmd = args.pop(0)
        else:
            cmd = ""
            args = []
        self._params["command"] = cmd
        self._params["args"] = args
        super().__init__(config, path)

    @property
    def full_command(self):
        return self._full_cmd

    @setting_property(default=False)
    def enabled(self):
        return self._params["enabled"]

    @enabled.setter
    @typecheck
    def enabled(self, value: bool):
        self._params["enabled"] = value

    @setting_property(default=100000)
    def max_countrate(self):
        return self._params["max_countrate"]

    @max_countrate.setter
    @typecheck
    def max_countrate(self, value: int):
        self._params["max_countrate"] = value

    @setting_property(default=[])
    def pixel_capacity_override(self):
        return self._params["pixel_capacity_override"]

    @pixel_capacity_override.setter
    @typecheck
    def pixel_capacity_override(self, value: list[dict]):
        self._params["pixel_capacity_override"] = value

    @setting_property(default=True)
    def abort_on_protection(self):
        return self._params["abort_on_protection"]

    @abort_on_protection.setter
    @typecheck
    def abort_on_protection(self, value: bool):
        self._params["abort_on_protection"] = value

    def __info__(self):
        params = dict(self._params, full_command=self.full_command)
        params.pop("command")
        params.pop("args")
        header = "Max. Countrate Protection\n"
        return header + tabulate(params) + "\n"
