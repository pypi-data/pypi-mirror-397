# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
SPEEDGOAT COUNTERS
"""

from bliss.shell.formatters import tabulate
from bliss.shell.formatters.table import IncrementalTable
from bliss.common.utils import RED
import re


class SpeedgoatHdwCounterController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._counters: dict[str, SpeedgoatHdwCounter] | None = None
        self._load()

    def __info__(self, debug=False):
        """Display list of all counters"""
        if self._counters is None:
            return "\n    No Counter in the model"

        if debug:
            lines = [["Name", "Signal Path", "Value", "Unit", "Description"]]
        else:
            lines = [["Name", "Value", "Unit", "Description"]]
        tab = IncrementalTable(lines, col_sep=" | ", flag="", lmargin="  ", align="<")
        for counter in self._counters.values():
            if debug:
                tab.add_line(
                    [
                        counter.name,
                        counter.path,
                        counter._formated_value,
                        counter.unit,
                        counter.description,
                    ]
                )
            else:
                tab.add_line(
                    [
                        counter.name,
                        counter._formated_value,
                        counter.unit,
                        counter.description,
                    ]
                )
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    def _load(self):
        self._counters = {}
        # Add custom counters defined in the YML file
        counters_yml = self._speedgoat._config.get("counters")
        if counters_yml is not None:
            for counter in counters_yml:
                # Set defaults if not set in the YML file
                counter.setdefault("description", None)
                counter.setdefault("unit", None)
                self._add_counter(
                    counter["name"],
                    counter["path"],
                    description=counter["description"],
                    unit=counter["unit"],
                )
        # Add counters defined in the Simulink file
        pattern = re.compile(r"^(?P<name>.+?)_counter_$")

        for signal_name, signal_obj in self._speedgoat._program.tree.signals.items():
            match = pattern.match(signal_obj.variable_name)
            if not match:
                continue

            name = match.group("name")

            counter_info = self._parse_signal_description(signal_obj.description)

            # Unit corresponding to the counter
            if "unit" in counter_info:
                # Format unit because of forbiden characters in Simulink
                unit = counter_info["unit"]
                unit = unit.replace("_per_", "/")
                unit = unit.replace("2", "^2")
                unit = unit.replace("3", "^3")
            else:
                unit = None

            # Description corresponding to the counter
            if "description" in counter_info:
                description = counter_info["description"]
            else:
                description = None

            # Used to specify the display "format" of the counter
            if "format_spec" in counter_info:
                format_spec = counter_info["format_spec"]
            else:
                format_spec = None

            self._add_counter(
                name,
                signal_obj.path[len(self._speedgoat._program.name) + 1 :],
                unit=unit,
                description=description,
                format_spec=format_spec,
            )

    def _parse_signal_description(self, desc_str: str) -> dict:
        """
        Parse a multiline description string containing lines like:
          _desc: ...
          _unit: ...
          _disp: ...
        Returns a dict without the leading underscores.
        """
        result = {}
        for line in desc_str.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue

            key, value = line.split(":", 1)
            key = key.strip().lstrip("_")  # remove leading underscore
            value = value.strip()

            result[key] = value

        return result

    def _add_counter(
        self, name, path, description=None, unit=None, format_spec=None, force=False
    ):
        # Verify signal path exists
        try:
            self._speedgoat.signal.get(path)
        except KeyError:
            print(f"{RED('WARNING')}: Counter '{name}' has not a valid path")
            return
        # Verify if counter name already exists
        if force is False and name in self._counters:
            print(
                f"{RED('WARNING')}: Counter '{name}' already exists, use force=True to override"
            )
            return
        # Create the Counter
        sp_counter = SpeedgoatHdwCounter(
            self._speedgoat,
            name,
            path,
            description=description,
            unit=unit,
            format_spec=format_spec,
        )
        setattr(self, name, sp_counter)
        self._counters[name] = sp_counter

    def _get_counter_from_full_path(self, full_path):
        for counter in self._counters.values():
            if counter._full_path == full_path:
                return counter
        raise KeyError(f"No counter with full_path={full_path}")


class SpeedgoatHdwCounter:
    """Speedgoat Counter - Has name, description, unit and value"""

    def __init__(
        self, speedgoat, name, path, description=None, unit=None, format_spec=None
    ):
        self._speedgoat = speedgoat
        self.name = name
        self.path = path
        self.description = description
        self.unit = unit
        self.format_spec = format_spec

    def __info__(self):
        lines = []
        lines.append(["Name", self.name])
        lines.append(["Description", self.description])
        lines.append(["Unit", self.unit])
        lines.append(["Path", self.path])
        lines.append(["", ""])
        lines.append(["Counter Value", self._formated_value])
        return tabulate.tabulate(lines, tablefmt="plain", stralign="right")

    @property
    def _full_path(self):
        return f"{self._speedgoat._program.name}/{self.path}"

    @property
    def value(self):
        return self._speedgoat.signal.get(self.path)

    @property
    def _formated_value(self):
        if self.format_spec is None:
            return repr(self.value)
        else:
            return f"{self.value:{self.format_spec}}"
