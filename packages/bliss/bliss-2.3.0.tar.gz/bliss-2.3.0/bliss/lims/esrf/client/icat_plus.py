import datetime
from collections.abc import Mapping
from collections.abc import Sequence

from pyicat_plus.client.main import IcatClient as _IcatClient

from bliss import __version__
from bliss import current_session
from bliss.lims.esrf.client.interface import Dataset
from bliss.lims.esrf.client.interface import DatasetId
from bliss.lims.esrf.client.interface import EsrfLimsClientInterface


class EsrfLimsIcatPlusClient(EsrfLimsClientInterface):
    """The value of all properties is retrieved from the Bliss session.
    This means the value is `None` when no session exists (e.g. using Bliss
    as a library). Exceptions are the proposal and the beamline which
    will fall back to the value set by the corresponding setters.
    """

    def __init__(
        self,
        metadata_urls: list[str] | None = None,
        elogbook_url: str | None = None,
        elogbook_token: str | None = None,
        metadata_queue: str | None = None,
        metadata_queue_monitor_port: int | None = None,
        elogbook_timeout: float | None = None,
        feedback_timeout: float | None = None,
        queue_timeout: float | None = None,
        beamline: str | None = None,
        proposal: str | None = None,
        elogbook_metadata: Mapping | None = None,
        update_metadata_urls: list[str] | None = None,
        update_metadata_queue: str | None = None,
        update_metadata_queue_monitor_port: int | None = None,
    ):
        """
        :param metadata_urls: URLs of the ActiveMQ message brokers to be used for creating ICAT datasets from a directory with metadata.
        :param elogbook_url: URL of the ICAT+ REST server to be used for sending text or images to the electronic logbook and get information about investigations.
        :param elogbook_token: Access token for restricted requests to `elogbook_url`.
        :param metadata_queue: Queue to be used when sending a message to `metadata_urls`.
        :param metadata_queue_monitor_port: REST server port to be used for monitor the `metadata_urls` ActiveMQ message brokers (same host as the message broker).
        :param elogbook_timeout: POST timeout for `elogbook_url`.
        :param feedback_timeout: GET timeout for `elogbook_url`.
        :param queue_timeout: Connection timeout for the ActiveMQ message brokers.
        :param beamline: Default beamline to be used as metadata when sending messages to `metadata_urls` or `elogbook_url`.
        :param proposal: Default proposal to be used as metadata when sending messages to `metadata_urls` or `elogbook_url`.
        :param elogbook_metadata: Default electronic logbook metadata to be used when sending messages to  `elogbook_url`.
        :param update_metadata_urls: URLs of the ActiveMQ message brokers to be used for update metadata of ICAT datasets.
        :param update_metadata_queue: Queue to be used when sending a message to `update_metadata_urls`.
        :param update_metadata_queue_monitor_port: REST server port to be used for monitor the `update_metadata_urls` ActiveMQ message brokers (same host as the message broker).
        """
        if elogbook_metadata is None:
            elogbook_metadata = {}
        elogbook_metadata.setdefault("software", "Bliss_v" + __version__)
        self.__current_proposal: str | None = None
        self.__current_beamline: str | None = None

        self._client = _IcatClient(
            metadata_urls=metadata_urls,
            elogbook_url=elogbook_url,
            elogbook_token=elogbook_token,
            metadata_queue=metadata_queue,
            metadata_queue_monitor_port=metadata_queue_monitor_port,
            elogbook_timeout=elogbook_timeout,
            feedback_timeout=feedback_timeout,
            queue_timeout=queue_timeout,
            beamline=beamline,
            proposal=proposal,
            elogbook_metadata=elogbook_metadata,
            update_metadata_urls=update_metadata_urls,
            update_metadata_queue=update_metadata_queue,
            update_metadata_queue_monitor_port=update_metadata_queue_monitor_port,
        )

    @property
    def current_proposal(self):
        if self.__current_proposal is None or current_session:
            self.__current_proposal = current_session.scan_saving.proposal_name
        return self.__current_proposal

    @current_proposal.setter
    def current_proposal(self, value: str | None):
        self.__current_proposal = value

    @property
    def current_beamline(self):
        if self.__current_beamline is None or current_session:
            self.__current_beamline = current_session.scan_saving.beamline
        return self.__current_beamline

    @current_beamline.setter
    def current_beamline(self, value: str | None):
        self.__current_beamline = value

    @property
    def current_dataset(self):
        return current_session.scan_saving.dataset_name

    @current_dataset.setter
    def current_dataset(self, value: str | None):
        pass

    @property
    def current_dataset_metadata(self):
        return current_session.scan_saving.dataset.get_current_icat_metadata()

    @current_dataset_metadata.setter
    def current_dataset_metadata(self, value: str | None):
        pass

    @property
    def current_collection(self):
        return current_session.scan_saving.collection

    @current_collection.setter
    def current_collection(self, value: str | None):
        pass

    @property
    def current_path(self):
        return current_session.scan_saving.icat_root_path

    @current_path.setter
    def current_path(self, value: str | None):
        pass

    def send_message(
        self,
        msg: str,
        msg_type: str | None = None,
        beamline: str | None = None,
        proposal: str | None = None,
        dataset: str | None = None,
        beamline_only: bool | None = None,
        editable: bool | None = None,
        formatted: bool | None = None,
        mimetype: str | None = None,
        **payload,
    ):
        if beamline_only:
            proposal = None
        elif proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        if beamline_only:
            dataset = None
        elif dataset is None:
            dataset = self.current_dataset
        self._client.send_message(
            msg,
            msg_type=msg_type,
            beamline=beamline,
            proposal=proposal,
            beamline_only=beamline_only,
            editable=editable,
            formatted=formatted,
            mimetype=mimetype,
            **payload,
        )

    def send_binary_data(
        self,
        data: bytes,
        mimetype: str | None = None,
        beamline: str | None = None,
        proposal: str | None = None,
        beamline_only: bool | None = None,
        **payload,
    ):
        if beamline_only:
            proposal = None
        elif proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        self._client.send_binary_data(
            data,
            mimetype=mimetype,
            beamline=beamline,
            proposal=proposal,
            beamline_only=beamline_only,
            **payload,
        )

    def send_text_file(
        self,
        filename: str,
        beamline: str | None = None,
        proposal: str | None = None,
        dataset: str | None = None,
        beamline_only: bool | None = None,
        **payload,
    ):
        if beamline_only:
            proposal = None
        elif proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        if beamline_only:
            dataset = None
        elif dataset is None:
            dataset = self.current_dataset
        self._client.send_text_file(
            filename,
            beamline=beamline,
            proposal=proposal,
            beamline_only=beamline_only,
            **payload,
        )

    def send_binary_file(
        self,
        filename: str,
        beamline: str | None = None,
        proposal: str | None = None,
        beamline_only: bool | None = None,
        **payload,
    ):
        if beamline_only:
            proposal = None
        elif proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        self._client.send_binary_file(
            filename,
            beamline=beamline,
            proposal=proposal,
            beamline_only=beamline_only,
            **payload,
        )

    def start_investigation(
        self,
        beamline: str | None = None,
        proposal: str | None = None,
        start_datetime=None,
        end_datetime=None,
    ):
        if proposal is None:
            proposal = self.current_proposal
        else:
            self.current_proposal = proposal
        if beamline is None:
            beamline = self.current_beamline
        else:
            self.current_beamline = beamline
        self._client.start_investigation(
            beamline=beamline,
            proposal=proposal,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    def store_dataset(
        self,
        beamline: str | None = None,
        proposal: str | None = None,
        dataset: str | None = None,
        path: str | None = None,
        metadata: dict = None,
        store_filename: str | None = None,
    ):
        if proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        if dataset is None:
            dataset = self.current_dataset
        if path is None:
            path = self.current_path
        if metadata is None:
            metadata = self.current_dataset_metadata
            if metadata is None:
                metadata = dict()
        self._client.store_dataset(
            beamline=beamline,
            proposal=proposal,
            dataset=dataset,
            path=path,
            metadata=metadata,
            store_filename=store_filename,
        )

    def store_processed_data(
        self,
        beamline: str | None = None,
        proposal: str | None = None,
        dataset: str | None = None,
        path: str | None = None,
        metadata: dict = None,
        raw: Sequence = tuple(),
        store_filename: str | None = None,
    ):
        """The 'raw' argument is shorthand for `metadata = {'input_datasets': ...}`."""
        if proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        if dataset is None:
            dataset = self.current_dataset
        if path is None:
            path = self.current_path
        if metadata is None:
            metadata = self.current_dataset_metadata
            if metadata is None:
                metadata = dict()
        self._client.store_processed_data(
            beamline=beamline,
            proposal=proposal,
            dataset=dataset,
            path=path,
            metadata=metadata,
            raw=raw,
            store_filename=store_filename,
        )

    def store_dataset_from_file(self, store_filename: str | None = None):
        self._client.store_dataset_from_file(store_filename=store_filename)

    def investigation_info(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> dict | None:
        return self._client.investigation_info(
            beamline,
            proposal,
            date=date,
            allow_open_ended=allow_open_ended,
            timeout=timeout,
        )

    def registered_dataset_ids(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> list[DatasetId] | None:
        return self._client.registered_dataset_ids(
            beamline,
            proposal,
            date=date,
            allow_open_ended=allow_open_ended,
            timeout=timeout,
        )

    def registered_datasets(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> list[Dataset] | None:
        return self._client.registered_datasets(
            beamline,
            proposal,
            date=date,
            allow_open_ended=allow_open_ended,
            timeout=timeout,
        )

    def investigation_info_string(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> str:
        return self._client.investigation_info_string(
            beamline,
            proposal,
            date=date,
            allow_open_ended=allow_open_ended,
            timeout=timeout,
        )

    def investigation_summary(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> list[tuple]:
        return self._client.investigation_summary(
            beamline,
            proposal,
            date=date,
            allow_open_ended=allow_open_ended,
            timeout=timeout,
        )

    def update_metadata(
        self,
        proposal: str = None,
        beamline: str = None,
        dataset_paths: str = None,
        metadata_name: str = None,
        metadata_value: str = None,
    ):
        if proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        self._client.update_metadata(
            proposal=proposal,
            beamline=beamline,
            dataset_paths=dataset_paths,
            metadata_name=metadata_name,
            metadata_value=metadata_value,
        )

    @property
    def expire_datasets_on_close(self) -> bool:
        return False

    @property
    def reason_for_missing_information(self) -> str:
        return "ICAT communication timeout"
