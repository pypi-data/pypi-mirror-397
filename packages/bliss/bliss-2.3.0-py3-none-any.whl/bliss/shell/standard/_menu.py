# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Standard functions provided to the BLISS shell.
"""

from __future__ import annotations

from bliss import current_session
from bliss.common.utils import ShellStr
from bliss.common import logtools
from bliss.shell.dialog import helpers as dialog_helpers
from bliss.common.capabilities import get_capability, MenuCapability
from bliss.shell.cli.user_dialog import UserSelect


# Expose this functions from this module
from bliss.shell.dialog.core import show_dialog  # noqa: E402,F401


def menu(obj=None, dialog_type: str | None = None, *args, **kwargs):
    """
    Display a dialog for acting on the object if this is implemented

    Args:
        obj: the object on which you want to operate, if no object is provided
             a complete list of available objects that have implemented some
             dialogs will be displayed.
        dialog_type: the dialog type that you want to display between one
             of the available. If this parameter is omitted and only one dialog
             is available for the given object than that dialog is diplayed,
             if instead more than one dialog is available will be launched a
             first selection dialog to choose from availables and than the
             selected one.

    Examples:

    >>> menu()  # will display all bliss objects that have dialog implemented

    >>> menu(wba)  # will launch the only available dialog for wba: "selection"

    >>> menu(wba, "selection")  # same as previous

    >>> menu(lima_simulator)  # will launch a selection dialog between available
    >>>                       # choices and than the selected one
    """
    if obj is None:
        names = set()
        # remove (_1, _2, ...) ptpython shell items that create false positive
        env = {
            k: v for (k, v) in current_session.env_dict.items() if not k.startswith("_")
        }

        for key, obj in env.items():
            menu_capability = get_capability(obj, MenuCapability)
            if menu_capability is not None:
                names.add(key)
                continue

            # NOTE: Backward compatibility with code based on BLISS API 2.2
            try:
                # intercepts functions like `ascan`
                if obj.__name__ in dialog_helpers.dialog.DIALOGS.keys():
                    names.add(key)
            except AttributeError:
                try:
                    # intercept class instances like `wago_simulator`
                    if obj.__class__.__name__ in dialog_helpers.dialog.DIALOGS.keys():
                        names.add(key)

                except AttributeError:
                    pass

        return ShellStr(
            "Dialog available for the following objects:\n\n" + "\n".join(sorted(names))
        )

    menu_capability = get_capability(obj, MenuCapability)
    if menu_capability is not None:
        menu_types = menu_capability.get_menu_types()
        if dialog_type is None and len(menu_types) > 0:
            # there are multiple dialogs => show main dialog to select sub-dialog
            title = f"Dialog Selection for {obj.name}"
            desc = [(v, str(v).capitalize()) for v in menu_types]
            dialog_type = show_dialog(
                UserSelect(name="selection", values=desc), title=title
            )
        try:
            menu_capability.show_menu(obj, dialog_type)
        except ValueError as exc:
            logtools.log_error(obj, "Error while showing menu", exc_info=True)
            return ShellStr(str(exc))
        return

    # NOTE: Backward compatibility with code based on BLISS API 2.2
    dialog = dialog_helpers.find_dialog(obj)
    if dialog is None:
        return ShellStr("No dialog available for this object")
    try:
        return dialog(dialog_type)
    except ValueError as exc:
        logtools.log_error(dialog, "Error while execution the dialog", exc_info=True)
        return ShellStr(str(exc))
