from __future__ import annotations
import abc
import enum
import gevent
import tblib
import traceback
import logging
import typing
import pint
from collections.abc import Callable
from typing_extensions import Unpack, TypedDict, TypeVar
from prompt_toolkit.application import current
from prompt_toolkit.application.current import AppSession

from bliss.scanning.scan import Scan
from bliss.config.beacon_object import BeaconObject, EnumProperty
from bliss.config.config_property import ConfigProperty
from bliss.config import static
from bliss.config.static import ConfigNode
from bliss.common.shell import is_shell_greenlet, transfer_eval_greenlet


_logger = logging.getLogger(__name__)


class ProcedureExecusionState(enum.Enum):
    NONE = "NONE"
    """No run yet"""

    ABORTED = "ABORTED"
    """Run was aborted"""

    FAILED = "FAILED"
    """Run have failed"""

    SUCCESSED = "SUCCESSED"
    """Run have successed"""


class ProcedureState(enum.Enum):
    STANDBY = "STANDBY"
    """Session scope procedure doing nothing"""

    DISABLED = "DISABLED"
    """Session scope procedure which can't be actually started"""

    RUNNING = "RUNNING"
    """Procedure doing something"""

    ABORTING = "ABORTING"
    """Procedure about to be aborted"""

    AWAITING_USER_INPUT = "AWAITING_USER_INPUT"
    """Temporarly interrupted running procedure until a user input is send"""

    UNKNOWN = "UNKNOWN"
    """The procedure have an undefined state.

    This only exists to share unexpected behavior with the sub systems.
    This indicates an implementation or environement problem.
    This should not be implementors directly.
    """


class BaseProcedure(abc.ABC):
    @property
    @abc.abstractmethod
    def state(self) -> ProcedureState:
        ...


class EmptyDict(TypedDict, total=True):
    pass


_P = TypeVar("_P", default=EmptyDict)


class SessionProcedure(typing.Generic[_P], BaseProcedure, BeaconObject):
    """Procedure which is available durring the whole BLISS session.

    It can be instanciated as a BLISS object in the yaml file.
    """

    def __init__(self, name: str, config: ConfigNode):
        BaseProcedure.__init__(self)
        BeaconObject.__init__(self, config)

        self.__prev_eval_g: gevent.Greenlet | None = None
        """Reference to the previous shell greenlet"""

        self._local_exception: BaseException | None = None
        self._starting: bool = False
        self._greenlet: gevent.Greenlet | None = None
        self._aborting: bool = False
        self._request_user_input: bool = False
        self._is_done = gevent.event.Event()
        self._is_validated = gevent.event.Event()
        self.__shell_validation: gevent.Greenlet | None = None
        if self._state == ProcedureState.UNKNOWN:
            self._state = ProcedureState.STANDBY

    name = ConfigProperty("name", readonly=True, vtype=str)
    """
    FIXME: The name should be handle by something else than ConfigProperty.
           That's system information.
    """

    _state = EnumProperty(
        "state",
        default=ProcedureState.STANDBY,
        unknown_value=ProcedureState.UNKNOWN,
        enum_type=ProcedureState,
    )

    previous_run_state = EnumProperty(
        "previous_run_state",
        default=ProcedureExecusionState.NONE,
        unknown_value=ProcedureExecusionState.NONE,
        enum_type=ProcedureExecusionState,
    )

    previous_run_exception = BeaconObject.property_setting(
        "previous_run_exception", None
    )

    previous_run_traceback = BeaconObject.property_setting(
        "previous_run_traceback", None
    )

    parameters = BeaconObject.property_setting("parameters", {})
    """Parameters are content evolving duing the prodecude.

    It have to stay light and serializable.
    For example, better to use reference that real data,
    """

    def get_parameter_as_device(self, key: str):
        hardware = self.parameters.get(key)
        if hardware is None:
            return None
        if not isinstance(hardware, dict):
            raise ValueError(f"Key {key} contains an unexpected type {type(hardware)}")
        objtype = hardware.get("__type__")
        if objtype != "hardware":
            raise ValueError(f"Key {key} contains an unexpected type {objtype}")

        objname = hardware.get("name")
        config = static.get_config()
        return config.get(objname)

    def update_parameters(self, **kwargs: Unpack[_P]):
        """Allow to update the parameters with automatic references.

        Scans are replaced by references. This can be extanded with
        other BLISS concepts.
        """
        values = dict(self.parameters)
        for k, v in kwargs.items():
            if isinstance(v, Scan):
                scan = v
                value = {
                    "__type__": "scan",
                    "key": scan._scan_data.key,
                }
            elif isinstance(v, pint.Quantity):
                value = {
                    "__type__": "quantity",
                    "scalar": v.magnitude,
                    "unit": str(v.unit),
                }
            elif isinstance(v, BaseException):
                value = {
                    "__type__": "exception",
                    "class": type(v).__name__,
                    "message": str(v),
                    "traceback": tblib.Traceback(v.__traceback__).to_dict(),
                }
            elif hasattr(v, "name"):
                value = {"__type__": "hardware", "name": v.name}
            else:
                value = v
            values[k] = value
        self.parameters = values

    @property
    def state(self):
        """Returns the actual state of the device"""
        return self._state

    def _get_state(self):
        if self._aborting:
            return ProcedureState.ABORTING
        if self._request_user_input:
            return ProcedureState.AWAITING_USER_INPUT
        if self._starting:
            return ProcedureState.RUNNING
        if self._greenlet is not None:
            return ProcedureState.RUNNING
        return ProcedureState.STANDBY

    def _update_state(self):
        s = self._get_state()
        if s != self._state:
            self._state = s

    @abc.abstractmethod
    def _run(self):
        ...

    def _done(self, greenlet: gevent.Greenlet):
        assert self._greenlet is not None
        self._aborting = False
        if self.__prev_eval_g is not None:
            self._greenlet.spawn_tree_locals["eval_greenlet"] = self.__prev_eval_g
            self.__prev_eval_g = None
        self._greenlet = None

        # Get the state of the execusion
        try:
            result = greenlet.get()
        except KeyboardInterrupt as e:
            self._local_exception = e
            run_state = ProcedureExecusionState.ABORTED
        except BaseException as e:
            _logger.error("Error while running %s", self.name, exc_info=True)
            run_state = ProcedureExecusionState.FAILED
            self._local_exception = e
            self.previous_run_exception = str(e)
            traceback_dict = tblib.Traceback(e.__traceback__).to_dict()
            self.previous_run_traceback = traceback_dict
        else:
            self._local_exception = None
            if isinstance(result, gevent.GreenletExit):
                run_state = ProcedureExecusionState.ABORTED
            else:
                run_state = ProcedureExecusionState.SUCCESSED
        if self.previous_run_state != run_state:
            self.previous_run_state = run_state

        self._update_state()
        self._is_done.set()

    def request_user_input(self):
        self._request_user_input = True

    def clear(self):
        """Clear information from the previous run"""
        self._request_user_input = False
        self.previous_run_state = ProcedureExecusionState.NONE
        self.previous_run_exception = None
        self.previous_run_traceback = None
        self.parameters = {}

    def run(self, wait=True):
        """
        Run the procedure.

        The application context is propagated to show user input
        by default (`wait=True`).

        Arguments:
            wait: Same behaviour as a scan, If `wait` is set to `True`, the procedure
                  is considered as forground and block the execution (the default)
                  until termination. If set to `False` it is considered as a background
                  task and is non blocking.
        """
        textblock_context_greenlet = False
        if wait:
            # If the procedure is started from the eval greenlet
            # we can display scan progress and umv with prompt toolkit
            app_session = current.get_app_session()
            textblock_context_greenlet = True
        else:
            app_session = None

        self.start(
            _textblock_context_greenlet=textblock_context_greenlet,
            _app_session=app_session,
        )

        if wait:
            try:
                self.wait()
            except (gevent.GreenletExit, gevent.Timeout, KeyboardInterrupt):
                self.abort()
                raise
        if self._local_exception:
            try:
                raise self._local_exception
            finally:
                self._local_exception = None

    def start(
        self, _textblock_context_greenlet=False, _app_session: AppSession | None = None
    ):
        """
        Start the procedure asynchronously.

        It's a non blocking call, for background executing.
        That is why the application context used for user inputs is not propagated.
        (i.e. no interactive user input should be displayed).
        """
        if self._greenlet is not None:
            raise RuntimeError("Procedure already running")
        self.__prev_eval_g = None
        self.clear()

        def do_run():
            # Propagate app session
            if _app_session is not None:
                current._current_app_session.set(_app_session)
            self._run()

        try:
            self._starting = True
            self._is_done.clear()
            self._update_state()
            name = self.name
            self._greenlet = gevent.spawn(do_run)
            self._greenlet.name = f"procedure-{name}"
            if _textblock_context_greenlet:
                self.__prev_eval_g = self._greenlet.spawn_tree_locals.get(
                    "eval_greenlet"
                )
                if self.__prev_eval_g is not None:
                    self._greenlet.spawn_tree_locals["eval_greenlet"] = self._greenlet
            self._greenlet.link(self._done)
        finally:
            self._starting = False
            self._update_state()

    def _wait_remote_validation(self):
        self._is_validated.clear()
        try:
            self._request_user_input = True
            self._update_state()
            self._is_validated.wait()
        finally:
            self._request_user_input = False
            self._update_state()

    def request_and_wait_validation(
        self, shell_func: Callable | None = None, *args, **kwargs
    ):
        """
        Call the function which ask validation to the user in the shell.

        This handle multimodal validation. The `shell_func` can be aborted
        if the validation is done remotely.

        Arguments:
            shell_func: The function containing user prompt validation
            args: Arguments to pass to `shell_func`
            kwargs: Keyboard arguments to pass to `shell_func`
        """
        if shell_func is None:
            # Only remote validation
            self._wait_remote_validation()
            return

        g_current = gevent.getcurrent()
        if not is_shell_greenlet(g_current):
            # The shell input can't be displayed
            self._wait_remote_validation()
            return

        app_session = current.get_app_session()

        def do_shell_func(*args, **kwargs):
            # Propagate app session
            current._current_app_session.set(app_session)
            shell_func(*args, **kwargs)

        self._request_user_input = True
        self._update_state()
        self.__shell_validation = gevent.spawn(do_shell_func, *args, **kwargs)
        try:
            with transfer_eval_greenlet(self.__shell_validation):
                self.__shell_validation.get()
        except gevent.GreenletExit:
            # It was aborted by a remote validation
            pass
        finally:
            self._request_user_input = False
            self.__shell_validation = None
            self._update_state()

    def _abort_shell_validation(self):
        """
        Abort the shell validation, if one.

        To be called when a validation is requested.
        """
        if self.__shell_validation is not None:
            self.__shell_validation.kill()

    def validate(self, new_parameters: dict | None):
        """Validate a pending user validation"""
        if new_parameters is not None:
            parameters = dict(self.parameters)
            parameters.update(new_parameters)
            self.parameters = parameters
        self._abort_shell_validation()
        self._is_validated.set()

    def abort(self):
        state = self._state
        if self._greenlet is None:
            if state in [ProcedureState.RUNNING, ProcedureState.AWAITING_USER_INPUT]:
                # Let's assume the state was not porperly reset
                self._update_state()
                return
            raise RuntimeError("Procedure not running")
        self._aborting = True
        self._update_state()
        self._greenlet.kill(block=False)

    def wait(self):
        self._is_done.wait()

    def __info__(self) -> str:
        lines: list[str] = []
        lines += (f"name:  {self.name}",)
        lines += (f"class: {type(self).__module__}.{type(self).__name__}",)
        lines += (f"state: {self.state.name}",)
        if self.previous_run_state != ProcedureExecusionState.NONE:
            lines += ("previous run:",)
            lines += (f"    state: {self.previous_run_state.name}",)
        if self.previous_run_exception is not None:
            message = str(self.previous_run_exception)
            message = message.replace("\n", "\n    | ")
            lines += ("    exception:",)
            lines += (f"    | {message}",)
            if self.previous_run_traceback is not None:
                lines += ("    traceback:",)
                tb = tblib.Traceback.from_dict(self.previous_run_traceback)
                trace = traceback.format_tb(tb)
                for t in trace:
                    t = t.rstrip("\n")
                    t = t.replace("\n", "\n    | ")
                    lines.append(f"    | {t}")
        return "\n".join(lines)
