# This file is part of the mechatronic project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from treelib import Tree

"""
SIGNALS
"""


class SpeedgoatHdwSignalController:
    def __init__(self, speedgoat):
        self._speedgoat = speedgoat
        self._system = speedgoat._system
        self._program = speedgoat._program
        self._signal_tree = speedgoat._program.tree.signals

    def __info__(self):
        self._tree.show()
        return ""

    @property
    def _tree(self):
        tree = Tree()
        root = self._program.name
        tree.create_node(root, root)

        for path in self._signal_tree:
            parts = path.split("/")
            parent = root
            for p in parts[1:]:
                node_id = "/".join(parts[: parts.index(p) + 1])  # unique identifier
                if not tree.contains(node_id):
                    tree.create_node(p, node_id, parent=parent)
                parent = node_id

        return tree

    def get(self, signal_path):
        return self._signal_tree[self._program.name + "/" + signal_path].value
