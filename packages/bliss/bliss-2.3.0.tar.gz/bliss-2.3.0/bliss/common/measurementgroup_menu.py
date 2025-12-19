from bliss.shell.dialog.core import show_dialog
from bliss.shell.cli.user_dialog import UserCheckBoxList, UserMsg
from bliss.common.capabilities import MenuCapability
from .measurementgroup import MeasurementGroup


def measurement_group_selection(mg: MeasurementGroup):

    values = []
    selection = []
    for fullname in mg.available:
        label = fullname
        values.append((fullname, label))
        if fullname in mg.enabled:
            selection.append(fullname)

    if len(values) == 0:
        msg = UserMsg(label="No available counters")
        show_dialog(msg, title=f"MeasurementGroup {mg.name}")
        return

    widget = UserCheckBoxList(label="Counters", values=values, defval=selection)
    result = show_dialog(
        [[widget]],
        title=f"MeasurementGroup {mg.name} Counter selection",
    )

    if result:
        selection = set(result[widget])
        for fullname, label in values:
            enabled = fullname in selection
            if enabled:
                mg.enable(fullname)
            else:
                mg.disable(fullname)


class MeasurementGroupMenuCapability(MenuCapability):
    def show_menu(self, obj: MeasurementGroup, menu_type: str | None = None):
        if menu_type is None:
            measurement_group_selection(obj)
        else:
            raise ValueError(f"No menu for {menu_type=}")
