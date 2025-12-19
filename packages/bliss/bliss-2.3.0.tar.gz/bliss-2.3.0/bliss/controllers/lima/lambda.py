# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from bliss.common.deprecation import deprecated_warning
import importlib

# Use importlib because lambda is a reserved word
mod = importlib.import_module(".lambda", "bliss.controllers.lima")

Camera = mod.Camera  # noqa

deprecated_warning(
    "Module",
    "bliss.controllers.lima.DETECTOR",
    replacement="bliss.controllers.lima.detectors.DETECTOR",
    since_version="2.3",
)
