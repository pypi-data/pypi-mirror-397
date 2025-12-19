"""
Helper to handle the beacon locks as a kind of ownership.

For now the lock is reentrant for a specific beacon connection.

As result a new connection have to be created for each owner.
"""

import os
import contextlib

from bliss.config.conductor.connection import Connection
from bliss.config.conductor import client


class AlreadyLockedDevices(RuntimeError):
    """Raised during locking, when a device(s) is already own by somebody"""

    def __init__(self, device_owners: dict[str, str]):
        self._device_owners: dict[str, str] = device_owners

    def __str__(self):
        devices = "', '".join(self._device_owners.keys())
        owners = "', '".join(self._device_owners.values())
        return f"Devices '{devices}' already owned by '{owners}'"


def lock(
    *devices,
    priority: int = 50,
    timeout=3.0,
    connection: Connection | None = None,
):
    """
    Lock a set of devices, if possible.

    Raises:
        AlreadyLockedDevices: If one of the devices is already owned.
    """
    if connection is None:
        connection = client.get_default_connection()
    try:
        client.lock(*devices, timeout=timeout, priority=priority, connection=connection)
    except RuntimeError:
        devices_name = [d.name for d in devices]
        result = connection.who_locked(*devices_name)
        raise AlreadyLockedDevices(result)


def unlock(
    *devices,
    priority: int = 50,
    timeout=3.0,
    connection: Connection | None = None,
):
    """Unlock a set of devices, if possible"""
    if connection is None:
        connection = client.get_default_connection()
    client.unlock(*devices, timeout=timeout, priority=priority, connection=connection)


@contextlib.contextmanager
def lock_context(*devices, owner: str, priority: int = 50, timeout: float = 3.0):
    """
    Context manager to own resource.

    .. code-block::

        with lock_context(lima):
            ct(lima)

    Arguments:
        owner: Name of the owner, in order to have an idea who is locking the devices.
        priority: Priority to check if the lock can be stolen
                (the biggest priority takes the lock)
        timeout: Time to wait in case the lock is not available
    """
    connection = Connection()
    connection.set_client_name(f"{owner},pid:{os.getpid()}")
    try:
        lock(*devices, priority=priority, timeout=timeout, connection=connection)
        try:
            yield
        finally:
            unlock(*devices, priority=priority, timeout=timeout, connection=connection)
    finally:
        connection.close()


def force_unlock(*devices):
    """
    Force to unlock devices.

    This can be used manually in case a procedure have terminated
    without releasing the lock by mistake (segmentation fault,
    network problems...)

    The user have to be careful that such procedure have physically
    really terminated before calling that function.
    """
    connection = Connection()
    try:
        lock(*devices, priority=999_999, timeout=10, connection=connection)
        unlock(*devices, connection=connection)
    finally:
        connection.close()


def is_locked_lazy(*devices) -> bool:
    """
    Lazy method to check if one of the devices are locked.

    It is a way to early skip some processing before trying to
    acquire the real lock.

    It can return `False` while some devices are locked.

    So the best way to use it is the following:

    .. code-block::

        if is_locked_lazy(my_detector):
            return

        ...

        try:
            with lock_context(my_detector):
                ...
        except AlreadyLockedDevices:
            ...

    The actual implementation is *not* lazy.
    But later it could only check the local process lock dependency.
    """
    connection = client.get_default_connection()
    all_locks = connection.who_locked()
    is_locked = [d in all_locks for d in devices]
    return any(is_locked)
