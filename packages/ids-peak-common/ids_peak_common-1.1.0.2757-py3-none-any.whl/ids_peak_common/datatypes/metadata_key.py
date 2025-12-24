from dataclasses import dataclass
from enum import Enum
from typing import Type, Any

from ids_peak_common.datatypes.geometry.rectangle import Rectangle


@dataclass(frozen=True)
class _MetadataKeyInfo:
    string_value: str
    type: Type[Any]


class MetadataKey(Enum):
    """
    Enumerates all compile-time known metadata keys.

    Each enum value carries both:
    - A string identifier (used internally in Metadata).
    - The expected Python type of its value.

    This makes it easy to use type-safe keys without an extra trait class.

    Example::

        key = MetadataKey.DEVICE_TIMESTAMP
        print(key.string_value) # outputs: device_timestamp
        print(key.type) # outputs: <class 'int'>

    .. ingroup:: ids_peak_common_python_types
    """

    DEVICE_TIMESTAMP = _MetadataKeyInfo("DeviceTimestamp", int)
    """
    Device-provided image acquisition timestamp in nanoseconds.

    The timestamp is expressed in nanoseconds and is relative to an
    unspecified reference point (t = 0). It does not represent an
    absolute wall-clock time, but instead the elapsed time since
    that reference. The difference between timestamps of consecutive
    images indicates the time interval between their recordings.
    """

    DEVICE_FRAME_ID = _MetadataKeyInfo("DeviceFrameID", int)
    """
    A sequentially incremented identifier for the frame.

    The frame ID is a sequentially incremented value that increases by one
    from one frame to the next. It serves as a means to detect missing or
    out-of-order frames in a stream. Once the maximum value supported by
    the underlying technology is reached, the frame ID wraps back to zero.
    The exact wrap-around point is not fixed and depends on the implementation.
    """

    BINNING_HORIZONTAL = _MetadataKeyInfo("BinningHorizontal", int)
    """
    Horizontal pixel binning factor.

    Indicates how many adjacent pixels are combined horizontally.
    """

    BINNING_VERTICAL = _MetadataKeyInfo("BinningVertical", int)
    """
    Vertical pixel binning factor.

    Indicates how many adjacent pixels are combined vertically.
    """

    ROI = _MetadataKeyInfo("Roi", Rectangle)
    """
    Region of interest applied to the image.

    Defines the rectangular area of the image that remains after
    processing steps such as cropping or scaling were applied.
    Coordinates and dimensions are expressed in pixels.
    """

    @property
    def string_value(self) -> str:
        """Return the string_value for this metadata key."""
        return self.value.string_value

    @property
    def type(self) -> Type[Any]:
        """Return the expected Python type for this metadata key."""
        return self.value.type

    def __str__(self) -> str:
        """
        Return a human-readable string of the MetadataKey object.
        """
        return f"{self.string_value} ({self.type.__name__})"

    def __repr__(self) -> str:
        """
        Return an unambiguous string of the MetadataKey object.
        """
        return (f"{self.__class__.__name__}.{self.name}"
                f"(string_value={self.value.string_value!r}, "
                f"type={self.value.type!r})")
