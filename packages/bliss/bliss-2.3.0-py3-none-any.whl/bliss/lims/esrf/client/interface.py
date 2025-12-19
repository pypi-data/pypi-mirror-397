import datetime
from abc import abstractmethod
from collections.abc import Sequence

from pyicat_plus.client.main import Dataset
from pyicat_plus.client.main import DatasetId


class EsrfLimsClientInterface:
    @abstractmethod
    def send_message(
        self,
        msg: str,
        msg_type: str | None = None,
        beamline: str | None = None,
        proposal: str | None = None,
        dataset: str | None = None,
        beamline_only: bool | None = None,
        **payload,
    ):
        """
        Send a message to the proposal or beamline e-logbook.

        :param msg: The message content.
        :param msg_type: {'comment', 'debug', 'info', 'error', 'commandLine'}, optional.
        :param beamline: The beamline name of the proposal or beamline e-logbook.
        :param proposal: The proposal name of the e-logbook. Ignored if `beamline_only` is True.
        :param dataset: The specific dataset name to link the message to.
        :param beamline_only: if `True`, the message will be stored in the beamline e-logbook.
        :param editable: Used with the `formatted` field, to determine the category of message. Annotation characterizes editable and unformatted messages, while Notification charaterizes non-editable and formatted messages.
        :param formatted: Used with the `editable` field, to determine the category of message. Annotation characterizes editable and unformatted messages, while Notification charaterizes non-editable and formatted messages.
        :param mimetype: {'text/plain', 'text/html'}, optional.
        :param payload: Additional payload for the message. It can contain tags (list of strings or list of dictionaries), the machine, the software.
        """
        pass

    @abstractmethod
    def send_binary_data(
        self,
        data: bytes,
        mimetype: str | None = None,
        beamline: str | None = None,
        proposal: str | None = None,
        beamline_only: bool | None = None,
        **payload,
    ):
        """
        Send an image in base64 format to the proposal or beamline e-logbook.

        :param data: The binary message content.
        :param mimetype: {'text/plain', 'text/html'}, optional.
        :param beamline: The beamline name of the proposal or beamline e-logbook.
        :param proposal: The proposal name of the e-logbook. Ignored if `beamline_only` is True.
        :param beamline_only: if `True`, the message will be stored in the beamline e-logbook.
        :param payload: Additional payload for the e-logbook message. It can contain tags (list of strings or list of dictionaries), the machine, the software.
        """
        pass

    @abstractmethod
    def send_text_file(
        self,
        filename: str,
        beamline: str | None = None,
        proposal: str | None = None,
        dataset: str | None = None,
        beamline_only: bool | None = None,
        **payload,
    ):
        """
        Send the content of a text file as a message to the proposal or beamline e-logbook.

        :param filename: The filename containing the message to be sent.
        :param beamline: The beamline name of the proposal or beamline e-logbook.
        :param proposal: The proposal name of the e-logbook. Ignored if `beamline_only` is True.
        :param beamline_only: if `True`, the message will be stored in the beamline e-logbook.
        :param payload: Additional payload for the e-logbook message. It can contain tags (list of strings or list of dictionaries), the machine, the software.
        """
        pass

    @abstractmethod
    def send_binary_file(
        self,
        filename: str,
        beamline: str | None = None,
        proposal: str | None = None,
        beamline_only: bool | None = None,
        **payload,
    ):
        """
        Send the content of a file as a binary image to the proposal or beamline e-logbook.

        :param filename: The filename of the image to be sent.
        :param beamline: The beamline name of the proposal or beamline e-logbook.
        :param proposal: The proposal name of the e-logbook. Ignored if `beamline_only` is True.
        :param beamline_only: if `True`, the message will be stored in the beamline e-logbook.
        :param payload: Additional payload for the e-logbook message. It can contain tags (list of strings or list of dictionaries), the machine, the software.
        """
        pass

    @abstractmethod
    def start_investigation(
        self,
        beamline: str | None = None,
        proposal: str | None = None,
        start_datetime=None,
        end_datetime=None,
    ):
        """
        Send a message to ActiveMQ to either synchronize the experiment session from the User Portal in ICAT or to create a test experiment session in ICAT.

        :param beamline: The beamline name of the proposal.
        :param proposal: The proposal name.
        :param start_datetime: The start date of the experiment session, timezone local time. Current date time by default.
        :param end_datetime: The end date of the experiment session, timezone local time.
        """
        pass

    @abstractmethod
    def store_dataset(
        self,
        beamline: str | None = None,
        proposal: str | None = None,
        dataset: str | None = None,
        path: str | None = None,
        metadata: dict = None,
        store_filename: str | None = None,
    ):
        """
        Request icat to store raw dataset.

        :param beamline str: beamline name like id01, id15a, bm18...
        :param proposal str: proposal name like in1169, blc14795, ihma429...
        :param str dataset: dataset name.
        :param str path: path to the raw dataset to store. Must be a folder.
        :param dict metadata: metadata to associate to the dataset. Must contains keys defined by the appropriate application definition from https://gitlab.esrf.fr/icat/hdf5-master-config/-/blob/88a975039694d5dba60e240b7bf46c22d34065a0/hdf5_cfg.xml.
        :param str store_filename: xml file with metadata to be stored.
        """
        pass

    @abstractmethod
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
        """
        Request icat to store a processed dataset.

        :param beamline str: beamline name like id01, id15a, bm18...
        :param proposal str: proposal name like in1169, blc14795, ihma429...
        :param str dataset: dataset name like sample_XYZ.
        :param str path: path to the processed dataset to store. Can be a file or a folder.
        :param dict metadata: metadata to associate to the dataset. Must contains keys defined by the appropriate application definition from https://gitlab.esrf.fr/icat/hdf5-master-config/-/blob/88a975039694d5dba60e240b7bf46c22d34065a0/hdf5_cfg.xml.
        :param tuple raw: Path to the raw dataset(s). Expects to be path to 'bliss dataset' folder(s). See https://confluence.esrf.fr/display/BM02KW/File+structure for
                          If processing rely on more than one dataset then all dataset folders must be provided.
        :param str store_filename: xml file with metadata to be stored.
        """
        pass

    @abstractmethod
    def store_dataset_from_file(self, store_filename: str | None = None):
        """
        Send a message to ActiveMQ to store a dataset and the associated metadata from a xml file stored on the disk.

        :param store_filename: The XML filename containing all dataset metadata.
        """
        pass

    @abstractmethod
    def investigation_info(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> dict | None:
        """
        Return the information of the experiment session corresponding to a beamline, proposal and date.

        :param beamline: The beamline name.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: If found, return the proposal, beamline, e-logbbok url and data portal url of the experiment session.
        """
        pass

    @abstractmethod
    def registered_dataset_ids(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> list[DatasetId] | None:
        """
        Return the dataset list of an experiment session.

        :param beamline: The beamline name of the proposal.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: The list of datasets (name and path).
        """
        pass

    @abstractmethod
    def registered_datasets(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> list[Dataset] | None:
        """
        Return the dataset information list of an experiment session.

        :param beamline: The beamline name of the proposal.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: The list of datasets (name, path, ICAT identifier, and :class:`.DatasetMetadata`).
        """
        pass

    @abstractmethod
    def investigation_info_string(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> str:
        """
        Return the experiment session information as a string.

        :param beamline: The beamline name.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: If found, return the experiment session information from the metadata catalog as a string.
        """
        pass

    @abstractmethod
    def investigation_summary(
        self,
        beamline: str,
        proposal: str,
        date: datetime.datetime | datetime.date | None = None,
        allow_open_ended: bool = True,
        timeout: float | None = None,
    ) -> list[tuple]:
        """
        Return the experiment session information as a `tuple`.

        :param beamline: The beamline name.
        :param proposal: The proposal name.
        :param date: The date of the proposal, current date by default.
        :param allow_open_ended: If `True`, enable to select an unofficial experiment session.
        :param timeout: Set a timeout for the ICAT request.
        :returns: If found, return the experiment session information from the metadata catalog as a `tuple`.
        """
        pass

    @abstractmethod
    def update_metadata(
        self,
        proposal: str = None,
        beamline: str = None,
        dataset_paths: str = None,
        metadata_name: str = None,
        metadata_value: str = None,
    ):
        """
        Update or create datasets metadata.

        :param proposal: The proposal name.
        :param beamline: The beamline name of the proposal.
        :param dataset_paths: Comma-separated list of the dataset locations.
        :param metadata_name: The name of the metadata to update.
        :param metadata_value: The new value of the metadata.
        """
        pass

    @property
    @abstractmethod
    def expire_datasets_on_close(self) -> bool:
        """
        A flag indicating whether the dataset expires when it is closed or if it is synchronized with the metadata catalog.
        """
        pass

    @property
    @abstractmethod
    def reason_for_missing_information(self) -> str:
        """
        A string explaining why some information is missing in the metadata catalog.
        """
        pass
