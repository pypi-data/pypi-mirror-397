"""
Helper to handle the beacon locks as a kind of ownership.

For now the lock is reentrant for a specific beacon connection.

As result a new connection have to be created for each owner.
"""

from bliss.config.conductor import client
from bliss.shell.formatters import tabulate


def lslock():
    """
    Display the active locks.
    """
    connection = client.get_default_connection()
    all_locks = connection.who_locked()
    if len(all_locks) == 0:
        print("No locks acquired")
        return

    print("The following locks are acquired")
    print()

    table: list[list[tuple[str, str] | tabulate.Cell]] = []

    table.append(
        [
            ("class:header", "Device/lock name"),
            ("class:header", "Owner"),
        ]
    )

    table.append(
        [
            tabulate.separator("-"),
            tabulate.separator("-"),
        ]
    )

    for name, owner in all_locks.items():
        table.append(
            [
                ("", name),
                ("", owner),
            ]
        )

    print(tabulate.tabulate(table))
    print()
