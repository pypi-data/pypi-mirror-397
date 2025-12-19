# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from tempfile import gettempdir

from bliss.scanning.scan_saving import ESRFScanSaving, ESRFDataPolicyEvent


def set_esrf_config(scan_saving, base_path):
    # Make sure all data saving mount points
    # have base_path as root in the session's
    # scan saving config (in memory)
    assert isinstance(scan_saving, ESRFScanSaving)
    scan_saving_config = scan_saving._scan_saving_config_node
    assert scan_saving_config is not None
    roots = ["inhouse_data_root", "visitor_data_root", "tmp_data_root"]
    default_path = gettempdir() + "/scans"
    for root in roots:
        for prefix in ["", "icat_"]:
            key = prefix + root
            mount_points = scan_saving_config.get(key, None)
            if mount_points is None:
                continue
            elif isinstance(mount_points, str):
                scan_saving_config[key] = mount_points.replace(default_path, base_path)
            else:
                for mp in mount_points:
                    mount_points[mp] = mount_points[mp].replace(default_path, base_path)


def set_esrf_data_policy(session, icat=True):
    """Setup the ESRF data policy for testing env.

    Arguments:
        icat: If true (the default), also setup ICAT
    """
    # SCAN_SAVING uses the `current_session`
    assert session.name == session.scan_saving.session

    # TODO: cannot use enable_esrf_data_policy directly because
    # we need to modify the in-memory config before setting the proposal.
    # If enable_esrf_data_policy changes however, we are in trouble.

    base_path = session.scan_saving.base_path
    session._set_scan_saving(cls=ESRFScanSaving)
    # base_path have to be restored after the swap of the class
    set_esrf_config(session.scan_saving, base_path)

    if icat:
        # session.scan_saving.get_path() sets the proposal to the default
        # proposal and notifies ICAT. When using the `icat_mock_client` fixture,
        # this will be the first event.
        session._emit_event(
            ESRFDataPolicyEvent.Enable,
            data_path=session.scan_saving.get_path(),
        )


def set_basic_data_policy(session):
    session.disable_esrf_data_policy()


def set_data_policy(session, policy):
    """
    Setup a session to be used with different kind of data policy.
    """
    if policy == "basic":
        set_basic_data_policy(session)
    elif policy == "esrf":
        set_esrf_data_policy(session)
    elif policy == "esrf-noicat":
        set_esrf_data_policy(session, icat=False)
    else:
        ValueError(policy, "Unsupported data policy")
