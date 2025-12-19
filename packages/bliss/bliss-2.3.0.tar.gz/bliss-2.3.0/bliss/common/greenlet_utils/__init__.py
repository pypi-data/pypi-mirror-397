# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from collections.abc import Callable
import contextlib
import gevent
from .killmask import (  # noqa: F401
    KillMask,
    AllowKill,
    protect_from_kill,
    protect_from_one_kill,
)


@contextlib.contextmanager
def timeout(seconds: float | None, message: Callable[[], str] | str | None = None):
    """
    Raise exception in the current greenlet after given `seconds` have elapsed.

    For the inside code of the context, a `gevent.Timeout` is raised.
    Then it is converted into a `TimeoutError` for the caller.

    This allow to avoid bubbling of `BaseException` in the user space,
    and support multiple context stacked together.

    An optional `message` can be set to specufy a message.
    It can be a string or a callable producing a string.

    .. code-block::

        # With a custom message
        with timeout(10.0, lambda: "Oups"):
            ...

        # With a custom message interpreted later
        with timeout(10.0, lambda: f"Error while waiting {something}"):
            ...

    Raises:
        TimeoutError
    """
    try:
        with gevent.Timeout(seconds) as local:
            yield
    except gevent.Timeout as exc:
        if exc is local:
            # It's our timeout
            if message is None:
                msg = f"{seconds} seconds"
            elif callable(message):
                msg = f"{message()} ({seconds} seconds)"
            elif message:
                msg = f"{str(message)} ({seconds} seconds)"
            raise TimeoutError(msg)
        raise exc
