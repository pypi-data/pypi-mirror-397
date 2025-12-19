from pyicat_plus.client.main import DatasetId  # noqa: F401

from bliss.config.static import get_config
from bliss.lims.esrf.client.null import EsrfLimsNullClient
from bliss.lims.esrf.client.icat_plus import EsrfLimsIcatPlusClient
from bliss.lims.esrf.client.interface import EsrfLimsClientInterface


def lims_client_is_disabled() -> bool:
    config = get_config().root.get("icat_servers")
    if config:
        return config.get("disable", False)
    else:
        return True


def lims_client_config(
    bliss_session: str, beamline: str, proposal: str | None = None
) -> dict:
    config = get_config().root.get("icat_servers")
    if config:
        config = dict(config)
        if proposal is not None:
            config["proposal"] = proposal
        config["beamline"] = beamline
        disable = config.pop("disable", False)
        return {"disable": disable, "kwargs": config}
    else:
        return {"disable": True}


def lims_client_from_config(config: dict) -> EsrfLimsClientInterface:
    if config["disable"]:
        return EsrfLimsNullClient(expire_datasets_on_close=False)
    else:
        return EsrfLimsIcatPlusClient(**config.get("kwargs", dict()))


def is_null_client(lims_client: EsrfLimsClientInterface) -> bool:
    return isinstance(lims_client, EsrfLimsNullClient)
