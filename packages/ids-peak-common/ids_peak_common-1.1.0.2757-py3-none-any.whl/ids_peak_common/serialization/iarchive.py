from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Union, TypeVar, Type


class IArchive(ABC):
    """
    Simplified interface for a hierarchical key-value archive system.

    Provides dict-like access with restricted value types:
    - bool, int, float, str
    - IArchive (nested)
    - Lists of the above

    .. ingroup:: ids_peak_common_python_serialization

    .. versionadded:: ids_peak_common 1.1
    """

    AllowedValue = Union[
        bool, int, float, str,
        List[bool], List[int], List[float], List[str], List["IArchive"]
    ]

    T = TypeVar("T", bound=AllowedValue)

    @abstractmethod
    def set(self, key: str, value: AllowedValue | IArchive) -> None:
        """
        Stores a value under the given key.

        :param key: Key to store the value under.
        :param value: The value to store (restricted types only).

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def get(self, key: str, datatype: Type[T]) -> T:
        """
        Retrieves the value stored under the given key.

        :param key: Key of the value to retrieve.
        :param datatype: The expected datatype of the value.
        :return: The stored value.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def get_archive(self, key: str) -> IArchive:
        """
        Retrieves the archive stored under the given key.

        :param key: Key of the archive to retrieve.
        :return: The stored archive.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        """
        Checks whether a given key exists in the archive.

        :param key: The key to check.
        :return: True if the key exists, False otherwise.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def keys(self) -> List[str]:
        """
        Returns all keys currently stored in the archive.

        :return: List of keys.

        .. versionadded:: ids_peak_common 1.1
        """
        pass

    @abstractmethod
    def create_archive(self) -> IArchive:
        """
        Creates a new, empty archive instance.

        .. versionadded:: ids_peak_common 1.1
        """
        pass
