from abc import ABC, abstractmethod
from typing import TextIO

from ids_peak_common.serialization.iarchive import IArchive


class ISerializer(ABC):
    """
    Interface for serializing data to an output stream.

    This interface defines a contract for writing structured or binary data
    into an output stream.

    Implementations of this interface are responsible for formatting and
    writing the contents of one or more archives to a given output destination.

    .. ingroup:: ids_peak_common_python_serialization

    .. versionadded:: ids_peak_common 1.1
    """

    @abstractmethod
    def write(self, archive: IArchive, stream: TextIO) -> None:
        """
        Serializes data and writes it to the specified output stream.

        :param archive: The archive which will be written to the output.
        :param stream: The output stream (e.g., file or buffer) to which
                       serialized data will be written.

        .. versionadded:: ids_peak_common 1.1
        """
        pass
