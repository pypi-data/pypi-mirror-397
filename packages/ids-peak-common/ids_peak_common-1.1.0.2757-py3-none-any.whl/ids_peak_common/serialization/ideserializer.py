from abc import ABC, abstractmethod
from typing import TextIO

from ids_peak_common.serialization.iarchive import IArchive


class IDeserializer(ABC):
    """
    Interface for deserializing structured data from an input stream into an archive.

    This interface defines the contract for reconstructing archive objects
    from serialized representations stored in a file, buffer, or other input source.

    .. ingroup:: ids_peak_common_python_serialization

    .. versionadded:: ids_peak_common 1.1
    """

    @abstractmethod
    def read(self, stream: TextIO) -> IArchive:
        """
        Deserializes data from the specified input stream into an archive.

        This method reads raw data from the provided input stream and converts it
        into a structured :class:`IArchive` object. The stream must be open, valid,
        and ready for reading before this function is called.

        :param stream: The input stream to read from.
                       It should point to the beginning of a valid archive format.
        :return: A deserialized IArchive instance.

        .. versionadded:: ids_peak_common 1.1
        """
        pass
