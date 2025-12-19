# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
SPEEDGOAT PARAMETERS
"""

import numpy as np
import bliss.config.static
from treelib import Tree
from bliss.shell.formatters.table import IncrementalTable


class SpeedgoatHdwParameterController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._system = speedgoat._system
        self._program = speedgoat._program
        self._param_tree = self._program.tree.params

        self._set_attr_root_params()
        self._set_default_params()

    # Display Tunnable parameters
    def __info__(self, debug=False):
        if self._root_params is None:
            return "\n    No parameters in the model"
        tab = IncrementalTable(
            [["Name", "Value"]], col_sep=" | ", flag="", lmargin="  ", align="<"
        )
        for parameter in self._root_params:
            tab.add_line([parameter, repr(getattr(self, parameter))])
        tab.resize(10, 100)
        tab.add_separator("-", line_index=1)
        mystr = "\n" + str(tab)
        return mystr

    # Used to automatically add "root parameters" as attributes for easy access/modification
    def _set_attr_root_params(self):
        for param_name in self._root_params:
            setattr(self.__class__, param_name, SpeedgoatParam(self, param_name))

    @property
    def _root_params(self):
        return [
            param
            for param in self._param_tree
            if (self._program.name not in param and param[-1] != "_")
        ]

    # Set default params as defined in the YML file
    def _set_default_params(self):
        params_yml = self._speedgoat._config.get("default_parameters")
        if params_yml is None:
            return

        for param in params_yml:
            try:
                if isinstance(param["value"], bliss.config.static.ConfigList):
                    self.set(param["path"], np.array(param["value"]))
                else:
                    self.set(param["path"], param["value"])
            except Exception:
                print(
                    f"Default parameter with path \"{param['path']}\" does not exist in the model"
                )

    @property
    def _tree(self):
        tree = Tree()
        root = self._program.name
        tree.create_node(root, root)

        for path in self._param_tree:
            parts = path.split("/")
            parent = root
            for i, p in enumerate(parts[1:], 1):  # start at index 1
                node_id = "/".join(
                    parts[: i + 1]
                )  # build unique identifier up to this level
                if not tree.contains(node_id):
                    tree.create_node(p, node_id, parent=parent)
                parent = node_id

        return tree

    def set(self, param_name, value):
        # Automatically add "model_name" if necessary
        if "/" in param_name:
            param_name = self._program.name + "/" + param_name
        self._param_tree[param_name].value = value

    def get(self, param_name):
        # Automatically add "model_name" if necessary
        if "/" in param_name:
            param_name = self._program.name + "/" + param_name
        return self._param_tree[param_name].value


class SpeedgoatParam:
    def __init__(self, param_ctl, param_name):
        self._param_ctl = param_ctl
        self._name = param_name

    def __get__(self, obj, objtype):
        return self._param_ctl.get(self._name)

    def __set__(self, obj, value):
        self._param_ctl.set(self._name, value)
