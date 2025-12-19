# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from collections.abc import Iterator
from contextlib import contextmanager
from enum import Enum, unique
import functools
from typing_extensions import Union
import logging
import re

from bliss import global_map, global_log
from bliss.common.expand import expandvars
from bliss.common.logtools import log_debug, log_warning
from bliss.common.utils import autocomplete_property, typecheck
from bliss.controllers.counter import CounterContainer, counter_namespace
from bliss.controllers.lima2.tabulate import tabulate
from bliss.controllers.lima2.controller import DetectorController
from bliss.controllers.lima2.settings import Settings, setting_property

import lima2.client.services as lima2_session


# Logger decorator
def logger(fn):
    def inner(self, *args, **kwargs):
        log_debug(self, f"Entering {fn.__name__}")
        to_execute = fn(self, *args, **kwargs)
        log_debug(self, f"Exiting {fn.__name__}")
        return to_execute

    return inner


@unique
class ProcPlugin(Enum):
    LEGACY = "LimaProcessingLegacy"
    SMX = "LimaProcessingSmx"
    XPCS = "LimaProcessingXpcs"
    FAILING = "LimaProcessingFailing"


def is_compatible(version: str, allowed: tuple[str]) -> bool:
    """Returns True if the version is compatible with the set of allowed versions."""
    pattern = re.compile(
        "(?P<prefix>([^-]+-)+)"
        "(?P<major>[0-9]+)\\."
        "(?P<minor>[0-9]+)\\."
        "(?P<patch>[0-9]+)"
        "(?P<extra>.*)?"
    )

    match = pattern.match(version)
    if match is None:
        raise ValueError(
            f"Version tag '{version}' doesn't match the expected "
            f"format '{pattern}'."
        )

    # Strip everything after the patch
    stripped = f"{match['prefix']}{match['major']}.{match['minor']}.{match['patch']}"
    if stripped in allowed:
        return True
    else:
        return False


def parse_port(port: str | int) -> int:
    if type(port) is str:
        return int(expandvars(port))
    else:
        return port


class Lima2(CounterContainer, Settings):
    """
    Lima2 device.
    Basic configuration:
        name: simulator
        class: Lima2
        conductor_host: localhost
        conductor_port: 58712
    """

    DEVICE_TYPE = "lima2"

    @logger
    def __init__(self, config):
        """Lima2 device.

        name -- the controller's name
        config -- controller configuration
        in this dictionary we need to have:
        conductor_host -- Conductor hostname
        conductor_port -- Conductor port
        """

        log_debug(self, f"Initialize Lima2 {config['name']}")

        self._config = config

        self._lima2 = lima2_session.init(
            hostname=self._config["conductor_host"],
            port=parse_port(self._config["conductor_port"]),
        )
        self._acquisition = None
        self._processing_plugins = {e.name: None for e in ProcPlugin}
        self._proc_plugin = None
        self._processing = None
        self._detector = None
        self._frame_cc = None
        self._in_connect = False

        # Enable logs from the lima2.client package
        logging.getLogger("lima2.client").setLevel(global_log._LOG_DEFAULT_LEVEL)

        # Single detector controller
        self._frame_cc = DetectorController(self)

        # Init Settings
        Settings.__init__(self, self._config, eager_init=False)

        # Global map
        global_map.register("lima2", parents_list=["global"])
        global_map.register(
            self,
            parents_list=["lima2", "controllers", "counters"],
        )

        self._initialized = False

        try:
            self.connect()
        except RuntimeError as e:
            log_debug(self, f"Can't connect to lima2 system: {e}")

    @contextmanager
    def connect_lock(self) -> Iterator[None]:
        if self._in_connect:
            raise RuntimeError(
                f"{self.name}.connect() called from within itself. "
                "Call it explicitly to get a trace."
            )
        self._in_connect = True
        try:
            yield
        finally:
            self._in_connect = False

    def connect(self) -> None:
        """Second step of the initialization. Raises if lima2 conductor or devices are offline.

        Allowed to fail once in __init__().
        Can be called explicitly to force a reconnect.
        """

        match self._lima2.connection_state():
            case lima2_session.ConnectionState.ONLINE:
                pass
            case lima2_session.ConnectionState.CONDUCTOR_OFFLINE:
                raise RuntimeError(
                    "Unable to connect to lima2 conductor at "
                    f"{self._lima2.session.hostname}:"
                    f"{self._lima2.session.port}"
                )
            case lima2_session.ConnectionState.DEVICES_OFFLINE:
                offline_devices = tuple(
                    name
                    for name, state in self._lima2.system_state()["devices"].items()
                    if state == "OFFLINE"
                )
                raise RuntimeError(f"Some lima2 devices are offline {offline_devices}")
            case _:
                raise NotImplementedError

        # Version check: raise here if the locally installed lima2-client package is
        # incompatible with the running lima2-conductor.
        self._lima2.handshake()

        with self.connect_lock():
            _, default_rcv_params = self._lima2.acquisition.default_params()

            # Create the user data structures to set detector params
            self._recvs_params = default_rcv_params
            self._ctrl_params = self._recvs_params

            import importlib

            # Detector plugin
            # NOTE: Loading the detector plugin is mandatory to use the controller, unlike
            # processing plugins which are all optional.
            try:
                plugin = self._lima2.detector.info()["plugin"].lower()
                module = importlib.import_module(
                    __package__ + ".detectors" + f".{plugin}"
                )

                version = self._lima2.detector.version()

                if not is_compatible(version, module.ALLOWED_VERSIONS):
                    raise RuntimeError(
                        f"The installed version of the bliss Lima2 '{plugin}' plugin is "
                        f"not compatible with the backend detector plugin version ({version}). "
                        f"Supported versions are {list(module.ALLOWED_VERSIONS)}."
                    )

                self._detector = module.Detector(self)
            except ImportError:
                log_warning(self, f"could not find a plugin for detector {plugin}")

            # Acquisition UI
            self._acquisition = Acquisition(self)

            # NOTE: this calls the self.proc_plugin setter, which initializes the
            # processing plugin.
            self._initialize_with_setting()

            self._initialized = True

    def _get_default_chain_counter_controller(self):
        """Return the default counter controller that should be used
        when this controller is used to customize the DEFAULT_CHAIN
        """
        return self._frame_cc

    # { required by AcquisitionObject
    @property
    def name(self):
        return self._config["name"]

    # }

    def _load_plugin(self, plugin: ProcPlugin):
        """Import a processing plugin module and instantiate its Processing object."""
        import importlib

        try:
            module = importlib.import_module(
                __package__ + ".processings" + f".{plugin.name.lower()}"
            )
        except ImportError:
            raise NotImplementedError(f"No plugin for {plugin.name} ({plugin.value})")

        # Version check
        # Raises if the backend has no matching processing pipeline.
        version = self._lima2.pipeline.version(processing_name=plugin.value)

        if not is_compatible(version, module.ALLOWED_VERSIONS):
            raise RuntimeError(
                f"The installed version of the bliss Lima2 '{plugin.name}' plugin is "
                f"not compatible with the running {plugin.value} processing backend version "
                f"({version}). Supported versions are {list(module.ALLOWED_VERSIONS)}.",
            )

        return module.Processing(self._config, pipeline=self._lima2.pipeline)

    @staticmethod
    def _auto_connect(method) -> None:
        """Attempt to call connect() if self._initialized is False.

        The difference with _auto_reconnect is that if the connection has
        already been established once, _auto_connect does not check again.

        Should be used when method needs connect() to have been called once, but
        a live connection isn't strictly required now.
        """

        @functools.wraps(method)
        def wrapper(self: "Lima2", *args, **kwargs):
            if not self._initialized:
                # Raises on failure
                self.connect()

            return method(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def _auto_reconnect(method) -> None:
        """
        Check the connection state before the method call, and if disconnected,
        attempt to reconnect.

        The difference with _auto_connect is that _auto_reconnect checks the
        end-to-end connection every time (-> more latency).

        Should be used for methods that absolutely need to have a live
        connection to lima2.
        """

        @functools.wraps(method)
        def wrapper(self: "Lima2", *args, **kwargs):
            # Query connection state every time
            conn_state = self._lima2.connection_state()

            if (
                not self._initialized
                or conn_state != lima2_session.ConnectionState.ONLINE
            ):
                # Raises on failure
                self.connect()

            return method(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def _auto_try_connect(method) -> None:
        """Attempt to call connect() if self._initialized is False.

        The difference with _auto_connect is that if connect() fails, the exception is
        absorbed.

        Should be used when `method` would like connect() to have been called, but doesn't
        critically depend on it.
        """

        @functools.wraps(method)
        def wrapper(self: "Lima2", *args, **kwargs):
            if not self._initialized:
                try:
                    self.connect()
                except RuntimeError:
                    pass

            return method(self, *args, **kwargs)

        return wrapper

    # { Implement CounterContainer
    @autocomplete_property
    @_auto_try_connect
    def counters(self):
        cnts = list()
        if self._detector:
            cnts += self._detector.counters
        if self._processing:
            cnts += self._processing.counters
        return counter_namespace(cnts)

    @property
    @_auto_try_connect
    def counter_groups(self):
        if self._detector and self._processing:
            groups = self._detector.counter_groups | self._processing.counter_groups
            groups["default"] = self.counters
            return counter_namespace(groups)
        else:
            return counter_namespace([])

    # }

    @autocomplete_property
    @_auto_connect
    def acquisition(self):
        """The acquisition user interface"""
        return self._acquisition

    @autocomplete_property
    @_auto_connect
    def processing(self):
        """The processing user interface"""
        return self._processing

    @autocomplete_property
    @_auto_connect
    def detector(self):
        """The detector (specific) user interface"""
        return self._detector

    def __info__(self):
        match self._lima2.connection_state():
            case lima2_session.ConnectionState.DEVICES_OFFLINE:
                return tabulate(
                    {
                        "Lima2": "OFFLINE",
                        "Reason": "Some devices offline",
                        "Details": self._lima2.system_state(),
                    }
                )
            case lima2_session.ConnectionState.CONDUCTOR_OFFLINE:
                return tabulate(
                    {
                        "Lima2": "OFFLINE",
                        "Reason": "Conductor is down",
                        "Details": {
                            "host": self._lima2.session.hostname,
                            "port": self._lima2.session.port,
                        },
                    }
                )
            case lima2_session.ConnectionState.ONLINE:
                try:
                    if not self._initialized:
                        self.connect()
                    det_info = self.det_info
                    res = f"{det_info['plugin']} ({det_info['model']})\n\n"
                    res += "Status:\n" + tabulate(self.det_status) + "\n\n"
                    # res += "Accumulation:\n" + tabulate(ctrl_params["accu"]) + "\n\n"
                    res += "Acquisition:\n" + self._acquisition.__info__() + "\n\n"
                    res += "Detector:\n\n" + self._detector.__info__() + "\n\n"
                    res += "Processing:\n\n" + self._processing.__info__()
                    return res
                except Exception as e:
                    log_warning(self, repr(e))
                    return repr(e)
            case _:
                raise NotImplementedError

    @property
    @_auto_reconnect
    def det_info(self):
        return self._lima2.detector.info()

    @property
    @_auto_reconnect
    def det_status(self):
        return self._lima2.detector.status()

    @property
    @_auto_reconnect
    def det_capabilities(self):
        return self._lima2.detector.capabilities()

    @setting_property(default="legacy")
    def proc_plugin(self) -> ProcPlugin:
        return self._proc_plugin

    @proc_plugin.setter
    def proc_plugin(self, plugin: Union[str, ProcPlugin]):
        if isinstance(plugin, str):
            try:
                plugin = ProcPlugin[plugin.upper()]
            except KeyError:
                raise KeyError(
                    f"No such processing plugin {plugin}. "
                    f"Try one of {list(ProcPlugin.__members__)}."
                ) from None

        # Lazy loading + initialization of the Processing instance
        if self._processing_plugins[plugin.name] is None:
            # NOTE: if the processing plugin fails to be loaded or initialized,
            # one of the following will raise.
            instance = self._load_plugin(plugin=plugin)
            instance._init_with_device(self)
            # ###
            self._processing_plugins[plugin.name] = instance

        self._processing = self._processing_plugins[plugin.name]
        self._proc_plugin = plugin

        return self._proc_plugin  # Required by Settings

    @property
    @_auto_reconnect
    def state(self) -> str:
        return self._lima2.acquisition.state()

    @property
    @_auto_reconnect
    def nb_frames_acquired(self) -> int:
        return self._lima2.acquisition.nb_frames_acquired()

    @property
    @_auto_reconnect
    def nb_frames_xferred(self) -> int:
        return self._lima2.acquisition.nb_frames_xferred()

    @logger
    def prepare(
        self,
        ctrl_params: dict = None,
        recvs_params: dict = None,
        procs_params: dict = None,
    ):
        if ctrl_params is None:
            ctrl_params = self._ctrl_params

        if recvs_params is None:
            recvs_params = self._recvs_params

        if procs_params is None:
            procs_params = self._processing._params

        # Automatic reset() attempt if last run failed
        if self._lima2.acquisition.failed():
            print(f"{self.name}: previous acquisition failed. Trying to recover...")
            self._lima2.acquisition.reset()
            print(f"{self.name}: recovered.")

        acq_uuid = self._lima2.acquisition.prepare(
            control=ctrl_params,
            receiver=recvs_params,
            processing=procs_params,
        )

        return acq_uuid

    @logger
    def start(self):
        self._lima2.acquisition.start()

    @logger
    def trigger(self):
        self._lima2.acquisition.trigger()

    @logger
    def stop(self):
        if self._lima2.acquisition.running():
            self._lima2.acquisition.stop()

    @logger
    def reset(self):
        self._lima2.acquisition.reset()

    @property
    @_auto_reconnect
    def current_pipeline(self):
        return self._lima2.pipeline.current_pipeline()

    @_auto_reconnect
    def pipelines(self):
        return self._lima2.pipeline.uuids()


# Acquisition user interface
class Acquisition(Settings):
    """
    Acquisition settings common to all detectors
    """

    def __init__(self, device: Lima2):
        self._lima2 = device._lima2
        self._params = device._ctrl_params["acq"]
        super().__init__(device._config)

    @setting_property(default=1)
    def nb_frames(self):
        return self._params["nb_frames"]

    @nb_frames.setter
    @typecheck
    def nb_frames(self, value: int):
        if value < 0:
            raise ValueError("nb_frames < 0")
        self._params["nb_frames"] = value

    @setting_property(default="internal")
    def trigger_mode(self):
        return self._params["trigger_mode"]

    @trigger_mode.setter
    @typecheck
    def trigger_mode(self, value: str):
        capabilities = self._lima2.detector.capabilities()
        trigger_modes = capabilities.get("trigger_modes", ["internal", "software"])
        if value not in trigger_modes:
            raise ValueError(
                f"'{value}' isn't a valid trigger mode. Use one of {trigger_modes}"
            )
        self._params["trigger_mode"] = value

    @setting_property(default=100e-3)
    def expo_time(self):
        value_us = self._params["expo_time"]
        return value_us * 1e-6

    @expo_time.setter
    @typecheck
    def expo_time(self, value: float):
        capabilities = self._lima2.detector.capabilities()
        range_ns = capabilities.get("expo_time_range", [1_000, 10_000_000_000])
        value_ns = int(value * 1e9)
        if not (range_ns[0] <= value_ns < range_ns[1]):
            raise ValueError(f"Out of range [{range_ns[0] / 1e9}, {range_ns[1] / 1e9})")
        self._params["expo_time"] = int(value_ns / 1e3)

    @setting_property(default=10e-6)
    def latency_time(self):
        value_us = self._params["latency_time"]
        return value_us * 1e-6

    @latency_time.setter
    @typecheck
    def latency_time(self, value: float):
        capabilities = self._lima2.detector.capabilities()
        range_ns = capabilities.get("latency_time_range", [1_000, 1_000_000_000])
        value_ns = int(value * 1e9)
        if not (range_ns[0] <= value_ns < range_ns[1]):
            raise ValueError(f"Out of range [{range_ns[0] / 1e9}, {range_ns[1] / 1e9})")
        self._params["latency_time"] = int(value_ns / 1e3)

    def __info__(self):
        return "Acquisition:\n" + tabulate(self._params) + "\n\n"
