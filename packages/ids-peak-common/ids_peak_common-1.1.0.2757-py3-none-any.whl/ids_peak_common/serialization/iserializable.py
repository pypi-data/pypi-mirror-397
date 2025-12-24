from abc import ABC, abstractmethod

from ids_peak_common.serialization.iarchive import IArchive


class ISerializable(ABC):
    """
    Interface for objects that can be serialized to and deserialized from an archive.

    Classes implementing this interface provide mechanisms to convert their internal state
    into a portable form using an IArchive, and restore it later from the same archive.

    .. ingroup:: ids_peak_common_python_serialization

    .. versionadded:: ids_peak_common 1.1
    """

    @abstractmethod
    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the current object into the provided archive.

        This method writes the internal state of the object into the given
        IArchive so that it can later be reconstructed using
        :meth:`deserialize`.

        :param archive: The archive to which the object data will be written.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def deserialize(self, archive: IArchive) -> None:
        """
        Deserializes the object's state from the provided archive.

        This method reads data from the given IArchive and reconstructs
        the internal state of the object.

        :param archive: The archive from which to read the object's data.

        .. versionadded:: ids_peak_common 1.1
        """
        pass
