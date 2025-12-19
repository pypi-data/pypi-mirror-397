# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import os
import pathlib
from contextlib import contextmanager

from bliss.testutils.process_utils import start_tango_server
from bliss.testutils.process_utils import start_rest_server


@contextmanager
def lima_simulator_context(personal_name: str, device_name: str):
    fqdn_prefix = f"tango://{os.environ['TANGO_HOST']}"
    device_fqdn = f"{fqdn_prefix}/{device_name}"
    admin_device_fqdn = f"{fqdn_prefix}/dserver/LimaCCDs/{personal_name}"

    conda_env = os.environ.get("LIMA_SIMULATOR_CONDA_ENV")
    if not conda_env:
        conda_env = None
    conda = os.environ.get("CONDA_EXE", None)
    if conda_env and conda:
        if os.sep in conda_env:
            option = "-p"
        else:
            option = "-n"
        cmdline_args = [
            conda,
            "run",
            option,
            conda_env,
            "--no-capture-output",
            "LimaCCDs",
        ]
    else:
        cmdline_args = ["LimaCCDs"]

    with start_tango_server(
        cmdline_args,
        personal_name,
        # "-v4",               # to enable debug
        device_fqdn=device_fqdn,
        admin_device_fqdn=admin_device_fqdn,
        state=None,
        check_children=conda_env is not None,
    ) as dev_proxy:
        yield device_fqdn, dev_proxy


@contextmanager
def lima2_simulator_context(
    personal_ctl_name: str,
    controller_device_name: str,
    personal_rcv_names: list[str],
    receiver_device_names: list[str],
    log_path: pathlib.Path,
    log_level: str = "warning",
):
    fqdn_prefix = f"tango://{os.environ['TANGO_HOST']}"
    device_fqdn = f"{fqdn_prefix}/{controller_device_name}"
    admin_device_fqdn = f"{fqdn_prefix}/dserver/lima2_tango/{personal_ctl_name}"
    secondary_devices_fqdns = [
        f"{fqdn_prefix}/{device_name}" for device_name in receiver_device_names
    ]

    # Execute the MPI program `lima2_tango` with the MPI program launcher with the following CLI:
    #
    #  mpiexec [global opts] [local opts for exec1] [exec1] [exec1 args] : [local opts for exec2] [exec2] [exec2 args] : ...

    conda_env = os.environ.get("LIMA2_SIMULATOR_CONDA_ENV")
    if not conda_env:
        conda_env = None
    conda = os.environ.get("CONDA_EXE", None)
    if conda_env and conda:
        if os.sep in conda_env:
            option = "-p"
        else:
            option = "-n"
        cmdline_args = [
            conda,
            "run",
            option,
            conda_env,
            "--no-capture-output",
            "mpiexec",
        ]
    else:
        cmdline_args = ["mpiexec"]

    def _log_args(name):
        return [
            "--log-level",
            log_level,
            "--log-file-path",
            str(log_path),
            "--log-file-filename",
            f"{name}_%N.log",
        ]

    # [global opts]
    #
    # Allow using MPI as root in CI (docker):
    #
    # 1. This fails with 'unrecognized argument allow-run-as-root' (same when used in [local opts]):
    #
    # cmdline_args += ["--allow-run-as-root"]
    #
    # 2. Use environment variables:
    #
    env = os.environ.copy()
    env["OMPI_ALLOW_RUN_AS_ROOT"] = "1"
    env["OMPI_ALLOW_RUN_AS_ROOT_CONFIRM"] = "1"

    # [local opts for exec1] [exec1] [exec1 args]
    cmdline_args += ["-n", "1", "lima2_tango", personal_ctl_name]
    cmdline_args += _log_args(personal_ctl_name)

    for personal_rcv_name in personal_rcv_names:
        # [local opts for exec2] [exec2] [exec2 args]
        cmdline_args += [":", "-n", "1", "lima2_tango", personal_rcv_name]
        cmdline_args += _log_args(personal_rcv_name)

    with start_tango_server(
        cmdline_args,
        device_fqdn=device_fqdn,
        admin_device_fqdn=admin_device_fqdn,
        secondary_devices_fqdns=secondary_devices_fqdns,
        state=None,
        secondary_state=None,
        check_children=conda_env is not None,
        env=env,
        timeout=60,
        num_retries=1,
    ) as dev_proxy:
        yield device_fqdn, dev_proxy


@contextmanager
def lima2_conductor_context(
    port: int, controller_device_name: str, receiver_device_names: list[str]
):
    conda_env = os.environ.get("LIMA2_SIMULATOR_CONDA_ENV")
    if not conda_env:
        conda_env = None
    conda = os.environ.get("CONDA_EXE", None)
    if conda_env and conda:
        if os.sep in conda_env:
            option = "-p"
        else:
            option = "-n"
        cmdline_args = [
            conda,
            "run",
            option,
            conda_env,
            "--no-capture-output",
            "lima2-conductor",
        ]
    else:
        cmdline_args = ["lima2-conductor"]

    # lima2-conductor start [OPTIONS] TANGO_HOST TOPOLOGY CONTROL_URL RECEIVER_URLS...

    # COMMAND
    cmdline_args += ["start"]
    # [OPTIONS]
    cmdline_args += [
        "--port",
        str(port),
        "--tango-timeout",
        "30",
        "--log-level",
        "warning",
    ]
    # TANGO_HOST TOPOLOGY CONTROL_URL
    cmdline_args += [
        os.environ["TANGO_HOST"],
        "round_robin",
        controller_device_name,
    ]
    # RECEIVER_URLS...
    cmdline_args += receiver_device_names

    get_state_url = f"http://localhost:{port}/state"
    expected_state = {
        "state": "IDLE",
        "runstate": "IDLE",
        "devices": {
            name: "IDLE" for name in [controller_device_name] + receiver_device_names
        },
    }

    with start_rest_server(
        cmdline_args,
        get_state_url,
        expected_state,
        timeout=30,
        check_children=conda_env is not None,
    ):
        yield


@contextmanager
def mosca_simulator_context(personal_name: str, device_name: str):
    fqdn_prefix = f"tango://{os.environ['TANGO_HOST']}"
    device_fqdn = f"{fqdn_prefix}/{device_name}"
    admin_device_fqdn = f"{fqdn_prefix}/dserver/SimulSpectro/{personal_name}"

    conda_env = os.environ.get("MOSCA_SIMULATOR_CONDA_ENV")
    if not conda_env:
        conda_env = None
    conda = os.environ.get("CONDA_EXE", None)
    if conda_env and conda:
        if os.sep in conda_env:
            option = "-p"
        else:
            option = "-n"
        cmdline_args = [
            conda,
            "run",
            option,
            conda_env,
            "--no-capture-output",
            "SimulSpectro",
        ]
    else:
        cmdline_args = ["SimulSpectro"]

    with start_tango_server(
        cmdline_args,
        personal_name,
        # "-v4",               # to enable debug
        device_fqdn=device_fqdn,
        admin_device_fqdn=admin_device_fqdn,
        state=None,
        check_children=conda_env is not None,
    ) as dev_proxy:
        yield device_fqdn, dev_proxy
