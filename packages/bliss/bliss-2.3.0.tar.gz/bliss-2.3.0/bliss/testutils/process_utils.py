import psutil
import gevent
import sys
import warnings
import time
import requests
import logging
import contextlib
import subprocess
from collections.abc import Generator
from bliss.tango.clients.utils import wait_tango_device

logger = logging.getLogger(__name__)


def eprint(*args):
    print(*args, file=sys.stderr, flush=True)


def wait_for(stream, target: bytes, timeout=None):
    """Wait for a specific bytes sequence from a stream.

    Arguments:
        stream: The stream to read
        target: The sequence to wait for
    """
    data = b""
    target = target.encode()
    while target not in data:
        char = stream.read(1)
        if not char:
            raise RuntimeError(
                "Target {!r} not found in the following stream:\n{}".format(
                    target, data.decode()
                )
            )
        data += char


@contextlib.contextmanager
def start_tango_server(
    cmdline_args: list[str],
    *deprecated_args: str,
    check_children: bool = False,
    env=None,
    num_retries: int = 3,
    **kwargs,
) -> Generator[None, None, None]:
    """
    Arguments:
        check_children: If true, children PID are also checked during termination.
    """

    _deprecated = False

    if isinstance(cmdline_args, str):
        _deprecated = True
        cmdline_args = [cmdline_args]

    if deprecated_args:
        _deprecated = True
        cmdline_args.extend(deprecated_args)

    if _deprecated:
        warnings.warn(
            "Passing positional command-line arguments to start_tango_server() is deprecated. "
            "Use start_tango_server(cmdline_args=[...]) instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    # If no args were provided at all
    if cmdline_args is None:
        cmdline_args = []

    device_fqdn = kwargs["device_fqdn"]
    exception = None
    err_msg = f"Tango devices related to {device_fqdn!r} cannot be pinged or do not have the correct state"
    for i in range(num_retries):
        proc = subprocess.Popen(cmdline_args, env=env)
        try:
            dev_proxy = wait_tango_device(**kwargs)
        except Exception as e:
            if (i + 1) == num_retries:
                warn_msg = f"{err_msg}: terminate and stop trying."
            else:
                warn_msg = f"{err_msg}: terminate and retry ..."
            logger.warning(warn_msg)
            print(warn_msg)  # So it is mixed with the server logs

            exception = e
            wait_terminate(proc, check_children=check_children)
        else:
            break
    else:
        raise RuntimeError(err_msg) from exception

    try:
        # FIXME: This have to be cleaned up by returning structured data
        # Expose the server PID as a proxy attribute
        object.__setattr__(dev_proxy, "server_pid", proc.pid)
        yield dev_proxy
    finally:
        wait_terminate(proc, check_children=check_children)


def wait_terminate(process, timeout=10, check_children=False):
    """
    Try to terminate a process then kill it.

    This ensure the process is terminated.

    Arguments:
        process: A process object from `subprocess` or `psutil`, or an PID int
        timeout: Timeout to way before using a kill signal
        check_children: If true, check children pid and force there termination
    Raises:
        gevent.Timeout: If the kill fails
    """
    children = []
    if isinstance(process, int):
        try:
            name = str(process)
            process = psutil.Process(process)
        except Exception:
            # PID is already dead
            return
    else:
        name = repr(" ".join(process.args))
        if process.poll() is not None:
            eprint(f"Process {name} already terminated with code {process.returncode}")
            return

    if check_children:
        if not isinstance(process, psutil.Process):
            process = psutil.Process(process.pid)
        children = process.children(recursive=True)

    process.terminate()
    try:
        with gevent.Timeout(timeout):
            # gevent timeout have to be used here
            # See https://github.com/gevent/gevent/issues/622
            process.wait()
    except gevent.Timeout:
        eprint(f"Process {name} doesn't finish: try to kill it...")
        process.kill()
        with gevent.Timeout(10):
            # gevent timeout have to be used here
            # See https://github.com/gevent/gevent/issues/622
            process.wait()

    if check_children:
        for i in range(10):
            _done, alive = psutil.wait_procs(children, timeout=1)
            if not alive:
                break
            for proc in alive:
                try:
                    if i < 3:
                        proc.terminate()
                    else:
                        proc.kill()
                except psutil.NoSuchProcess:
                    pass
        else:
            raise RuntimeError(
                "Timeout expired after 10 seconds. Process %s still alive." % alive
            )


@contextlib.contextmanager
def start_process(
    cmdline_args: list[str], check_children=False, env=None
) -> Generator[None, None, None]:
    """
    Arguments:
        check_children: If true, children PID are also checked during the terminating
    """
    proc = None
    try:
        proc = subprocess.Popen(cmdline_args, env=env)
        yield
    finally:
        if proc is not None:
            wait_terminate(proc, check_children=check_children)


@contextlib.contextmanager
def start_rest_server(
    cmdline_args: list[str],
    get_url: str,
    expected_response: dict,
    timeout: int = 10,
    check_children=False,
    env=None,
) -> Generator[None, None, None]:
    """
    Arguments:
        check_children: If true, children PID are also checked during the terminating
    """
    with start_process(cmdline_args, check_children=check_children, env=env):
        _wait_rest_server(get_url, expected_response, timeout)
        yield


def _wait_rest_server(get_url: str, expected_response: dict, timeout: int = 10) -> None:
    t0 = time.time()
    response = None
    exception = None
    while True:
        try:
            response = requests.get(get_url, timeout=timeout).json()
        except Exception as ex:
            response = None
            exception = ex
        if (time.time() - t0) > timeout:
            if response is None:
                raise TimeoutError(f"Failed to GET {get_url!r}") from exception
            else:
                raise TimeoutError(
                    f"Response of GET {get_url!r} is\n {response}\ninstead of\n {expected_response}"
                )
        if response is not None:
            if response == expected_response:
                break
        time.sleep(0.5)
