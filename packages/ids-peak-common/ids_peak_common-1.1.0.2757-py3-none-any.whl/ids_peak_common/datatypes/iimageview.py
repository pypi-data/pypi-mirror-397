from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
from ids_peak_common.datatypes.geometry.size import Size
from ids_peak_common.datatypes.pixelformat import PixelFormat
from ids_peak_common.datatypes.metadata import Metadata


class IImageView(ABC):
    """
    Interface for viewing image pixel data from arbitrary sources, for example a camera buffer.

    .. ingroup:: ids_peak_common_python_types
    """

    @abstractmethod
    def to_numpy_array(self, copy: bool = True) -> np.ndarray:
        """
        Returns the image data as a NumPy array.

        By default, the data is copied. Setting copy=False makes the array share memory with
        the internal buffer, so any changes to the array will be reflected in the image data.

        The dimensionality of the returned NumPy array varies according to the pixel format:
        * Packed formats produce a 1-dimensional array.
        * Single-channel formats (for example, Mono8) produce a 2-dimensional array with shape (height, width).
        * Multi-channel formats (for example, RGB8) produce a 3-dimensional array with shape (height, width, num_channels).

        :param copy: Whether to copy the data. Default is True.
        :return: The image data as a NumPy array.
        """
        pass

    @abstractmethod
    def to_memoryview(self) -> memoryview:
        """
        Return a zero-copy memoryview of the image data.

        The returned memoryview provides direct access to the underlying image data
        without copying data. Modifying the memoryview will modify the image data itself.
        Ensure that the image view and its underlying buffer remain valid before
        accessing or using the memoryview.
        """
        pass

    @property
    @abstractmethod
    def pixel_format(self) -> PixelFormat:
        """
        Returns the pixel format of the image.
        """
        pass

    @property
    @abstractmethod
    def size(self) -> Size:
        """
        Returns the image dimensions as a Size object.
        """
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        """
        Returns the width of the image in pixels.
        """
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        """
        Returns the height of the image in pixels.
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> Metadata:
        """
        Returns the metadata object which can be used to retrieve or set metadata belonging to the image.
        """
        pass
