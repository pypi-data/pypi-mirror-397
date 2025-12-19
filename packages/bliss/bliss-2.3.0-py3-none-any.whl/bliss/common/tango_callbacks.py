# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Class to simplify dealing with tango events.
"""

from __future__ import annotations

import tango
import enum
import logging
import gevent
import dataclasses
import typing
from bliss.common.logtools import log_warning
from collections.abc import Callable
from bliss.common.utils import Undefined
from bliss.common.tango import DeviceProxy, read_limits
from tango import is_numerical_type


_logger = logging.getLogger(__name__)


def _is_int_str(v: str) -> bool:
    try:
        int(v)
    except ValueError:
        return False
    return True


def _is_float_str(v: str) -> bool:
    try:
        float(v)
    except ValueError:
        return False
    return True


def _as_float_else_none(v) -> float | None:
    try:
        return float(v)
    except ValueError:
        return None


@dataclasses.dataclass
class _TangoCallbackDesc:
    """Describe a user callback with a cache to store the last polled value."""

    callback: Callable[[str, typing.Any], None]
    """Callback to cal when the attribute change"""

    last_polled_value: typing.Any = Undefined


@dataclasses.dataclass
class _TangoCallbackEvent:
    attr_name: str
    """Name of the monitored tango attribute"""

    value_callback_desc: _TangoCallbackDesc | None = None
    """Callback to call when the `value` attribute change"""

    wvalue_callback_desc: _TangoCallbackDesc | None = None
    """Callback to call when the `w_value` attribute change"""

    event_id: int | None = None
    """When the event was registered to tango"""

    polled: bool = False
    """Is the attribute polled"""

    def clear(self):
        """Clear the cached memory"""
        if self.value_callback_desc:
            self.value_callback_desc.last_polled_value = Undefined
        if self.wvalue_callback_desc:
            self.wvalue_callback_desc.last_polled_value = Undefined


class TangoConfigType(enum.Enum):
    LIMITS = enum.auto()
    """Monitor the change on limits"""


@dataclasses.dataclass
class _TangoCallbackConfigEvent:
    attr_name: str
    """Name of the monitored tango attribute"""

    callback_descs: dict[TangoConfigType, _TangoCallbackDesc]
    """Callback to cal when the attribute change"""

    event_id: int | None = None
    """When the event was registered to tango"""

    polled: bool = False
    """Is the attribute polled"""

    def clear(self):
        """Clear the cached memory"""
        for callback_desc in self.callback_descs.values():
            callback_desc.last_polled_value = Undefined


class TangoCallbacks:
    """Helper to deal with tango events.

    It tried to handle the different kind of behaviour we can have to receive
    change event from tango. Else finally fallback with a client side polling.

    Actually only events on the attribute change, and on the limits change are
    supported.

    .. code-block:: python

        def on_state_changed(attr_name, value):
            print(attr_name, value)

        def on_limits_changed(attr_name, value):
            print(f"{attr_name} min: {value[0]} max: {value[1]}")

        proxy = DeviceProxy("foo/bar/buz")
        cb = TangoCallbacks(proxy)
        cb.add_value_callback("state", on_state_changed)
        cb.add_wvalue_callback("position", on_target_changed)
        cb.add_limits_callback("position", on_limits_changed)
        ...
        cb.stop()
    """

    SERVER_SIDE_POLLING = 1000  # in ms or None
    """
    Default server-side polling period used when the polling was not enabled.
    """

    CLIENT_SIDE_POLLING = 1000  # in ms
    """
    Default client-side polling.

    Now the client side polling is never used, because the server-side
    polling is turned on if needed. The code is still there in case we have some
    troubles and we have to enable it back.
    """

    def __init__(self, device_proxy: DeviceProxy):
        self._device_proxy = device_proxy
        self._name = device_proxy.dev_name()
        self._connected: bool = False
        self._watchdog: gevent.Greenlet = gevent.spawn(self._try_device)
        self._watchdog.name = f"{__name__}.{self._name}"
        self._events: dict[str, _TangoCallbackEvent] = {}
        self._config_events: dict[str, _TangoCallbackConfigEvent] = {}
        self._poller: gevent.Greenlet | None = None

    def add_callback(self, attr_name: str, callback: Callable[[str, typing.Any], None]):
        """
        Register a callback to the value change of the `attr_name`.

        Deprecated: Prefer to use `add_value_callback`.
        """
        self.add_value_callback(attr_name, callback)

    def add_value_callback(
        self, attr_name: str, callback: Callable[[str, typing.Any], None]
    ):
        """Register a callback to the value change of the `attr_name`."""
        assert not self._connected
        # Normalize to lower case, to be consistent with att_name from tango event callback
        attr_name = attr_name.lower()
        event_callback = self._events.get(attr_name)
        if event_callback is not None:
            event_callback.value_callback_desc = _TangoCallbackDesc(callback)
        else:
            new_event_callback = _TangoCallbackEvent(
                attr_name=attr_name, value_callback_desc=_TangoCallbackDesc(callback)
            )
            self._events[attr_name] = new_event_callback

    def add_wvalue_callback(
        self, attr_name: str, callback: Callable[[str, typing.Any], None]
    ):
        """Register a callback to the value change of the `attr_name`."""
        assert not self._connected
        # Normalize to lower case, to be consistent with att_name from tango event callback
        attr_name = attr_name.lower()
        event_callback = self._events.get(attr_name)
        if event_callback is not None:
            event_callback.wvalue_callback_desc = _TangoCallbackDesc(callback)
        else:
            new_event_callback = _TangoCallbackEvent(
                attr_name=attr_name, wvalue_callback_desc=_TangoCallbackDesc(callback)
            )
            self._events[attr_name] = new_event_callback

    def add_limits_callback(
        self,
        attr_name: str,
        callback: Callable[[str, tuple[float | None, float | None]], None],
    ):
        """Register a callback to the limits change of the `attr_name`."""
        self.add_config_callback(attr_name, TangoConfigType.LIMITS, callback)

    def add_config_callback(
        self,
        attr_name: str,
        config_type: TangoConfigType,
        callback: Callable[[str, typing.Any], None],
    ):
        assert not self._connected
        # Normalize to lower case, to be consistent with att_name from tango event callback
        attr_name = attr_name.lower()
        change_callbacks = self._config_events.get(attr_name)
        if change_callbacks is None:
            change_callbacks = _TangoCallbackConfigEvent(
                attr_name=attr_name, callback_descs={}
            )
            self._config_events[attr_name] = change_callbacks
        change_callbacks.callback_descs[config_type] = _TangoCallbackDesc(callback)

    def _connect(self):
        """Try to connect the tango device

        raises:
            tango.ConnectionFailed: Connection have failed
            tango.DevFailed: Another tango thing have failed
            Exception: Another thing have failed
        """
        _logger.info("Trying to connect to %s", self._name)
        self._device_proxy.ping()
        self._subscribe_device()
        self._connected = True

    def _disconnect(self):
        """Disconnect from tango device"""
        self._unsubscribe_device()
        self._connected = False

    def stop(self):
        """Terminate the callbacks.

        The object should not be used anymore.
        """
        if self._watchdog is not None:
            self._watchdog.kill()
        self._watchdog = None
        if self._poller is not None:
            self._poller.kill()
        self._poller = None
        self._disconnect()

    def _try_device(self):
        """Watch dog trying to reconnect to the remote hardware if it was
        disconnected"""
        while True:
            if not self._connected:
                try:
                    self._connect()
                except Exception:
                    _logger.info(
                        "Could not connect to %s. Retrying in 10s",
                        self._name,
                        exc_info=True,
                    )
            gevent.sleep(10)

    def _subscribe_device(self):
        """Subscribe events for this device"""
        for event_callback in self._events.values():
            try:
                if self.SERVER_SIDE_POLLING is None:
                    raise RuntimeError("Server-side events turned off by the client")
                event_id = self._force_subscribe_event(
                    event_callback.attr_name,
                    tango.EventType.CHANGE_EVENT,
                    self._push_event,
                )
                event_callback.event_id = event_id
            except Exception:
                _logger.info(
                    "Could not subscribe to property %s %s. Fallback with polling.",
                    self._name,
                    event_callback.attr_name,
                    exc_info=True,
                )
                self._subscribe_polling_attribute(event_callback.attr_name)

        for config_event_callback in self._config_events.values():
            try:
                if self.SERVER_SIDE_POLLING is None:
                    raise RuntimeError("Server-side events turned off by the client")
                event_id = self._force_subscribe_event(
                    config_event_callback.attr_name,
                    tango.EventType.ATTR_CONF_EVENT,
                    self._push_config_event,
                )
                config_event_callback.event_id = event_id
            except Exception:
                _logger.info(
                    "Could not subscribe to property %s %s. Fallback with polling.",
                    self._name,
                    config_event_callback.attr_name,
                    exc_info=True,
                )
                self._subscribe_polling_config_attribute(
                    config_event_callback.attr_name
                )

    def _unsubscribe_device(self):
        """Unsubscribe registred events for this daiquiri hardware"""
        for event_callback in self._events.values():
            event_callback.polled = False
            if event_callback.event_id is None:
                continue
            try:
                self._device_proxy.unsubscribe_event(event_callback.event_id)
            except Exception:
                _logger.info("Couldnt unsubscribe from %s", event_callback.attr_name)
            else:
                event_callback.event_id = None

        for config_event_callback in self._config_events.values():
            config_event_callback.polled = False
            if config_event_callback.event_id is None:
                continue
            try:
                self._device_proxy.unsubscribe_event(config_event_callback.event_id)
            except Exception:
                _logger.info(
                    "Couldnt unsubscribe from %s", config_event_callback.attr_name
                )
            else:
                config_event_callback.event_id = None

    def _get_dev_error_reason(self, e: tango.DevFailed) -> str:
        if hasattr(e, "reason"):
            # Not working with pytango 9.3.6
            return e.reason
        elif hasattr(e, "args"):
            # Working with pytango 9.3.6
            if isinstance(e.args, tuple):
                err = e.args[0]
                if isinstance(err, tango.DevError):
                    return err.reason
        return "UNKONWN"

    def _force_subscribe_event(
        self, attr_name: str, event_type: tango.EventType, callback
    ):
        """Force polling a tango attribute.

        Trying first to subscribe.

        If it fails, setup the server side events.

        raises:
            tango.DevFailed: If the subscription failed
            RuntimeError: If the event configuration have failed
        """
        obj = self._device_proxy

        def update_server_polling():
            is_polled = obj.is_attribute_polled(attr_name)
            if not is_polled:
                _logger.warning(
                    "Server-side polling not enabled for %s.%s", self._name, attr_name
                )
                _logger.warning(
                    "Active server-side polling for %s.%s (%sms)",
                    self._name,
                    attr_name,
                    self.SERVER_SIDE_POLLING,
                )
                obj.poll_attribute(attr_name, self.SERVER_SIDE_POLLING)

        def update_server_event_config():
            info: tango.AttributeInfoEx = obj.get_attribute_config(attr_name)
            changes = []

            valid_period = _is_int_str(info.events.per_event.period)
            if not valid_period:
                changes += ["period"]
                info.events.per_event.period = f"{self.SERVER_SIDE_POLLING}"

            if is_numerical_type(info.data_type):
                valid_rel_change = _is_float_str(info.events.ch_event.rel_change)
                valid_abs_change = _is_float_str(info.events.ch_event.abs_change)
                if not valid_abs_change and not valid_rel_change:
                    changes += ["rel_change"]
                    info.events.ch_event.rel_change = "0.001"

            if changes != []:
                msg = " + ".join(changes)
                _logger.info("Active %s for %s %s", msg, self._name, attr_name)
                try:
                    info.name = attr_name
                    obj.set_attribute_config(info)
                except tango.DevFailed:
                    raise RuntimeError(
                        f"Failed to configure events {self._name} {attr_name}"
                    )

        try:
            result = obj.subscribe_event(
                attr_name,
                event_type,
                callback,
                green_mode=tango.GreenMode.Gevent,
            )
        except tango.DevFailed as e:
            reason = self._get_dev_error_reason(e)
            if reason in [
                "API_EventPropertiesNotSet",
                "API_AttributePollingNotStarted",
            ]:
                pass
            else:
                raise
        else:
            return result

        update_server_polling()
        update_server_event_config()

        _logger.info("Retry using event for %s.%s", self._name, attr_name)
        for i in range(3):
            # Sometimes it stuck, no idea why
            # Retry with a gevent timeout in case
            try:
                with gevent.Timeout(1.0, TimeoutError):
                    return obj.subscribe_event(
                        attr_name,
                        event_type,
                        callback,
                        green_mode=tango.GreenMode.Gevent,
                    )
            except TimeoutError:
                continue
            else:
                pass

    def _setup_poller(self):
        """Spawn a poller greenlet if not yet done."""
        if self._poller is None:
            self._poller = gevent.spawn(self._poll_attributes)
            self._poller.name = f"{__name__}.{self._name}"

    def _subscribe_polling_attribute(self, attr_name: str):
        obj = self._device_proxy
        log_warning(
            obj,
            "Use client-side polling for %s %s. To remove this warning, the server-side polling can be enabled.",
            self._name,
            attr_name,
        )
        self._setup_poller()
        self._events[attr_name].polled = True

    def _subscribe_polling_config_attribute(self, attr_name: str):
        obj = self._device_proxy
        log_warning(
            obj,
            "Use client-side polling for %s %s. To remove this warning, the server-side polling can be enabled.",
            self._name,
            attr_name,
        )
        self._setup_poller()
        self._config_events[attr_name].polled = True

    def _poll_attributes(self):
        _logger.info("Start client side polling for %s", self._name)
        while True:
            something_to_poll = False
            for event_callback in self._events.values():
                if event_callback.polled:
                    something_to_poll = True
                    attr = self._device_proxy.read_attribute(event_callback.attr_name)

                    value_callback_desc = event_callback.value_callback_desc
                    if value_callback_desc is not None:
                        value = attr.value
                        if value_callback_desc.last_polled_value != value:
                            value_callback_desc.last_polled_value = value
                            # Second check in case of change during context switch
                            if event_callback.polled:
                                value_callback_desc.callback(
                                    event_callback.attr_name, value
                                )

                    wvalue_callback_desc = event_callback.wvalue_callback_desc
                    if wvalue_callback_desc is not None:
                        wvalue = attr.w_value
                        if wvalue_callback_desc.last_polled_value != wvalue:
                            wvalue_callback_desc.last_polled_value = wvalue
                            # Second check in case of change during context switch
                            if event_callback.polled:
                                wvalue_callback_desc.callback(
                                    event_callback.attr_name, wvalue
                                )

            for config_event_callback in self._config_events.values():
                if config_event_callback.polled:
                    something_to_poll = True
                    config = self._device_proxy.get_attribute_config(
                        config_event_callback.attr_name
                    )
                    for (
                        config_kind,
                        callback_desc,
                    ) in config_event_callback.callback_descs.items():
                        value = self._read_value_from_config(config_kind, config)
                        if callback_desc.last_polled_value != value:
                            callback_desc.last_polled_value = value
                            # Second check in case of change during context switch
                            if config_event_callback.polled:
                                callback_desc.callback(
                                    config_event_callback.attr_name, value
                                )
            if not something_to_poll:
                break
            gevent.sleep(self.CLIENT_SIDE_POLLING / 1000.0)

        _logger.info("Stop client side polling for %s", self._name)
        for event_callback in self._events.values():
            event_callback.clear()
        for config_event_callback in self._config_events.values():
            config_event_callback.clear()

        self._poller = None

    def _read_value_from_config(
        self, config_kind: TangoConfigType, config: tango.AttributeInfo
    ):
        if config_kind == TangoConfigType.LIMITS:
            return read_limits(config)
        raise ValueError(f"Unexpected value config_kind. Found: '{config_kind}'")

    def _push_event(self, event: tango.EventData):
        """Callback triggered when the remote tango hardware fire an event"""
        try:
            self._protected_push_event(event)
        except Exception:
            _logger.error("Error while processing push_event", exc_info=True)

    def _protected_push_event(self, event: tango.EventData):
        """Callback triggered when the remote tango hardware fire an event

        Any exceptions raised are catched by `_push_event`.
        """
        if not self._connected:
            return

        if event.errors:
            error = event.errors[0]
            _logger.info(f"Error in push_event for {event.attr_name}: {error.desc}")
            # if error.reason == 'API_EventTimeout':
            self._disconnect()
            return

        if event.attr_value is not None:
            event_callback = self._events.get(event.attr_value.name, None)
            if event_callback is not None:
                if event_callback.wvalue_callback_desc:
                    wvalue = event.attr_value.w_value
                    if event_callback.wvalue_callback_desc.last_polled_value != wvalue:
                        event_callback.wvalue_callback_desc.last_polled_value = wvalue
                        event_callback.wvalue_callback_desc.callback(
                            event_callback.attr_name, wvalue
                        )
                if event_callback.value_callback_desc:
                    event_callback.value_callback_desc.callback(
                        event_callback.attr_name, event.attr_value.value
                    )

    def _push_config_event(self, event: tango.AttrConfEventData):
        """Callback triggered when the remote tango hardware fire an event"""
        try:
            self._protected_push_config_event(event)
        except Exception:
            _logger.error("Error while processing push_config_event", exc_info=True)

    def _protected_push_config_event(self, event: tango.AttrConfEventData):
        """Callback triggered when the remote tango hardware fire an event

        Any exceptions raised are catched by `_push_config_event`.
        """
        if not self._connected:
            return

        if event.errors:
            error = event.errors[0]
            _logger.info(
                f"Error in push_config_event for {event.attr_name}: {error.desc}"
            )
            # if error.reason == 'API_EventTimeout':
            self._disconnect()
            return

        config = event.attr_conf
        config_event_callback = self._config_events.get(config.name.lower(), None)
        if config_event_callback is not None:
            for (
                config_kind,
                callback_desc,
            ) in config_event_callback.callback_descs.items():
                value = self._read_value_from_config(config_kind, config)
                if callback_desc.last_polled_value != value:
                    callback_desc.last_polled_value = value
                    callback_desc.callback(config_event_callback.attr_name, value)
