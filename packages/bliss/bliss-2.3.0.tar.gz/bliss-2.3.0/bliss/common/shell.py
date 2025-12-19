# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Shell related helpers which can be also used by non related shell module,
like controllers.
"""

from __future__ import annotations

import contextlib
import gevent


def is_shell_greenlet(greenlet: gevent.greenlet | gevent.Greenlet) -> bool:
    """
    Return true if this greenlet have the ownership to print interactive
    content in the shell.
    """
    g = gevent.getcurrent()
    if not isinstance(g, gevent.Greenlet):
        return False
    eval_greenlet = g.spawn_tree_locals.get("eval_greenlet", None)
    return eval_greenlet is g


def is_eval_greenlet() -> bool:
    """
    Return true if the current greenlet have the ownership to print interactive
    content in the shell.

    Deprecated: Prefer using `is_shell_greenlet`.
    """
    g = gevent.getcurrent()
    return is_shell_greenlet(g)


def set_shell_greenlet(greenlet: gevent.Greenlet):
    """
    Set the shell greenlet ownership from this greenlet.

    This is an internal helper which have to be used carefully.
    Prefer to use a `transfer_eval_greenlet`.
    """
    if not isinstance(greenlet, gevent.Greenlet):
        raise TypeError(
            "The green can't be used as shell greenlet because it's not a gevent greenlet"
        )
    greenlet.spawn_tree_locals["eval_greenlet"] = greenlet


def clear_shell_greenlet(greenlet: gevent.Greenlet):
    """
    Remove the shell greenlet ownership from this greenlet.

    This is an internal helper which have to be used carefully.
    Prefer to use a `transfer_eval_greenlet`.
    """
    if not isinstance(greenlet, gevent.Greenlet):
        raise TypeError(
            "The green can't be used as shell greenlet because it's not a gevent greenlet"
        )
    greenlet.spawn_tree_locals["eval_greenlet"] = None


@contextlib.contextmanager
def transfer_eval_greenlet(new_greenlet: gevent.Greenlet):
    """
    Propagate the `eval_greenlet` of the current greenlet to the given greenlet.

    This can be used the new greenlet is blocking and when you want it to
    dipslay text UI.

    At the end of the context, the `eval_greenlet` is restored.

    IMPORTANT, this must be done just after the creation of the new greenlet,
    if there is IO access in between, the new greenlet maybe have already
    started.

    .. code-block::

        with transfer_eval_greenlet(my_new_greenlet):
            my_new_greenlet.wait()
    """
    g = gevent.getcurrent()
    if not is_shell_greenlet(g):
        # Nothing to propagate
        yield
        return

    try:
        set_shell_greenlet(new_greenlet)
        yield
    finally:
        clear_shell_greenlet(new_greenlet)
        set_shell_greenlet(g)
