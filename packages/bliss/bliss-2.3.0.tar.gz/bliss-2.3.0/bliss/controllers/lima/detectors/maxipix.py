# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from ..lima_base import CameraBase


class Camera(CameraBase):
    @property
    def synchro_mode(self):
        return "TRIGGER"

    def to_dict(self, *args, **kwargs):
        kwargs["include_properties"] = (
            "config_path",
            "config_name",
            "energy_threshold",
        )
        return super().to_dict(*args, **kwargs)
