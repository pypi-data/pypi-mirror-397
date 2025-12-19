# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import sys
import traceback


def capture_error_msg(with_tb=True):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_value:
        tb = traceback.TracebackException(
            exc_type, exc_value, exc_traceback, capture_locals=False
        )
        if with_tb:
            lines = tb.format()
        else:
            lines = tb.format_exception_only()

        return "".join(lines)
