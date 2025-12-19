from bliss.shell.cli.user_dialog import UserChoice, UserMsg
from bliss.shell.dialog.core import show_dialog
from bliss.common.utils import flatten
from bliss.common.capabilities import MenuCapability
from .white_beam_attenuator import WhiteBeamAttenuator


def wba_menu(obj: WhiteBeamAttenuator):
    """Whitebeam attenuator dialog for foil selection"""
    dialogs = []
    attenuators = [att["attenuator"] for att in obj.attenuators]  # objects
    attenuator_names = [att.name for att in attenuators]  # names
    for i, attenuator in enumerate(attenuators):
        positions_list = attenuator.positions_list
        indexes = {pos["label"]: i for i, pos in enumerate(positions_list)}
        values = [(pos["label"], pos["description"]) for pos in positions_list]
        axis = positions_list[0]["target"][0]["axis"]
        defval_label = attenuator.position  # actual position in string form
        try:
            defval = indexes[defval_label]  # numeric index of position
        except KeyError:
            defval = 0
            dialogs.append([UserMsg(label="WARNING! Attenuator position is UNKNOWN")])

        dialogs.append(
            [
                UserChoice(
                    label=f"Attenuator motor {axis.name}", values=values, defval=defval
                )
            ]
        )
    choices = show_dialog(dialogs, title="Attenuator foil selection")
    if choices:
        # exclude 'dynamically' added UserMsg returned values for 'Attenuator position is UNKNOWN'
        values = zip(
            attenuator_names,
            [
                retval
                for widget, retval in choices.items()
                if not isinstance(widget, UserMsg)
            ],
        )
        obj.move(flatten(values))
    return obj


class WBAMenuCapability(MenuCapability):
    def show_menu(self, obj: WhiteBeamAttenuator, menu_type: str | None = None):
        if menu_type is None:
            wba_menu(obj)
        else:
            raise ValueError(f"No menu for {menu_type=}")
