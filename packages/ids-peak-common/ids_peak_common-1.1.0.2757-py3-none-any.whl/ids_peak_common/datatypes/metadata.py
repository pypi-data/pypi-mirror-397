from typing import Any, Dict, Type, TypeVar, List

from ids_peak_common.datatypes.metadata_key import MetadataKey
from ids_peak_common.exceptions import OutOfRangeException, InvalidCastException

T = TypeVar("T")


class Metadata:
    """
    A type-safe container for metadata key-value pairs.

    This class provides a flexible mechanism for storing and retrieving metadata:
    - Arbitrary runtime keys (string string_values).
    - Strongly typed keys defined in a schema.

    Values are stored in a Python dictionary but accessed with additional
    safety checks to ensure type correctness.

    Example usage::

        metadata = Metadata()
        metadata.set_value_by_key(MetadataKey.DEVICE_FRAME_ID, 1)
        print(metadata.get_value_by_key(MetadataKey.DEVICE_FRAME_ID)) # outputs: 1
        print(metadata.has_entry_by_key(MetadataKey.DEVICE_FRAME_ID)) # outputs: True

     .. ingroup:: ids_peak_common_python_types
    """

    def __init__(self) -> None:
        """Initialize an empty metadata container."""
        self._data: Dict[str, Any] = {}

    def set_value_by_name(self, key: str, value: Any) -> None:
        """
        Store a value using a string-based key.

        :param key: Runtime string string_value.
        :param value: Value to store.
        """
        self._data[key] = value

    def has_entry_by_name(self, key: str) -> bool:
        """
        Check if a string key is present in the metadata.

        :param key: The metadata key.
        :return: True if the key exists, False otherwise.
        """
        return key in self._data

    def try_get_value_by_name(self, key: str) -> Any:
        """
        Retrieve a value by string key, returning None if not found.

        :param key: The metadata key.
        :return: The stored value if found, otherwise None.
        """
        return self._data.get(key, None)

    def get_value_by_name(self, expected_type: Type[T], key: str) -> T:
        """
        Retrieve the value for a key and validate that it is of the expected type.

        :param expected_type: The expected type of the stored value.
        :param key: The metadata key.
        :raises OutOfRangeException: If the key does not exist.
        :raises InvalidCastException: If the stored type does not match.
        :return: The stored value cast to the expected type.
        """
        if key not in self._data:
            raise OutOfRangeException(f"There is no value named '{key}'")

        value = self._data[key]
        if not isinstance(value, expected_type):
            raise InvalidCastException(
                f"Value for key '{key}' is of type {type(value).__name__}, "
                f"expected {expected_type.__name__}"
            )
        return value

    def set_value_by_key(self, key: MetadataKey, value: Any) -> None:
        """
        Store a value using a strongly typed metadata key.

        :param key: A MetadataKey object containing key name and expected type.
        :param value: The value to store.
        :raises InvalidCastException: If the value type does not match the trait type.
        """
        if not isinstance(value, key.type):
            raise InvalidCastException(
                f"Value for key '{key.string_value}' must be of type {key.type.__name__}, "
                f"got {type(value).__name__}"
            )
        self._data[key.string_value] = value

    def has_entry_by_key(self, key: MetadataKey) -> bool:
        """
        Check if a strongly typed metadata key is present and matches the expected type.

        :param key: A MetadataKey object.
        :return: True if the key exists and type matches, False otherwise.
        """
        if key.string_value not in self._data:
            return False
        return isinstance(self._data[key.string_value], key.type)

    def get_value_by_key(self, key: MetadataKey) -> Any:
        """
        Retrieve the value of a strongly typed metadata key.

        :param key: A MetadataKey object.
        :raises OutOfRangeException: If the key does not exist.
        :raises InvalidCastException: If the type does not match.
        :return: The stored value.
        """
        if key.string_value not in self._data:
            raise OutOfRangeException(f"Key '{key.string_value}' not found")

        value = self._data[key.string_value]
        if not isinstance(value, key.type):
            raise InvalidCastException(
                f"Value for key '{key.string_value}' is of type {type(value).__name__}, "
                f"expected {key.type.__name__}"
            )
        return value

    def get_key_names(self) -> List[str]:
        """
        Returns a list of metadata key names.

        :return: A list of metadata key names
        """
        return list(self._data.keys())

    def __eq__(self, other: Any) -> bool:
        """
        Check if two metadata are equal.

        :param other: Another Metadata object

        :return: True if metadata are equal, False otherwise
        """
        if isinstance(other, Metadata):
            return self._data == other._data
        return False

    def __ne__(self, other: Any) -> bool:
        """
        Check if two metadata are not equal.

        :param other: Another metadata object

        :return: True if metadata are not equal, False otherwise
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        """
        Return a human-readable string of metadata keys and values.

        Example:
            { "DeviceFrameID": 42, "DeviceTimestamp": 1695472000, "custom_data": "xyz" }
        """
        items = [f'"{k}": {v!r}' for k, v in self._data.items()]

        return f"( {', '.join(items)} )"

    def __repr__(self) -> str:
        """
        Return an unambiguous string of the Metadata object.
        """
        return f"{self.__class__.__name__}{str(self)}"
