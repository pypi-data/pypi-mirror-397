from __future__ import annotations

from typing import Union, Any

from ids_peak_common import exceptions
from ids_peak_common._internal.utils import is_equal, validate_parameter_types


class Size:
    """
    A size consists of width and height where width and height have to be greater than or equal to zero.

    .. ingroup:: ids_peak_common_python_types_geometry
    """

    def __init__(self, width: Union[int, float], height: Union[int, float]):
        """
        Size constructor from width and height.

        :param width: Width of the size.
        :param height: Height of the size.

        :raises OutOfRangeException: If width or height is less than zero.
        """
        validate_parameter_types(width, height, accepted_types=(int, float))
        if width < 0:
            raise exceptions.OutOfRangeException("Parameter width has to be greater or equal to zero.")
        if height < 0:
            raise exceptions.OutOfRangeException("Parameter height has to be greater or equal to zero.")

        self._width = width
        self._height = height

    def __eq__(self, other: Any) -> bool:
        """
        Check if two Size objects are equal.

        :param other: Another Size object OR List of width and height [width, height] OR Tuple of width and height (width, height)

        :return: True if both objects are equal, False otherwise.
        """
        if isinstance(other, Size):
            return is_equal(self.width, other.width) and is_equal(self.height, other.height)
        if isinstance(other, (list, tuple)):
            if len(other) != 2:
                return False
            return is_equal(self.width, other[0]) and is_equal(self.height, other[1])

        return False

    def __ne__(self, other: Any) -> bool:
        """
        Check if two Size objects are not equal.

        :param other: Another Size object OR List/Tuple with width and height.

        :return: True if both objects are not equal, False otherwise.
        """
        return not self == other

    def __str__(self) -> str:
        """
        Returns a string representation of the Size object.

        :return: String representation of the Size object.
        """
        return f"(width={self.width}, height={self.height})"

    def __repr__(self) -> str:
        """
        Return an unambiguous string of the Size object.
        """
        return f"{self.__class__.__name__}{str(self)}"

    @property
    def width(self) -> Union[int, float]:
        """
        Get the width of the size.

        :return: The width value.
        """
        return self._width

    @property
    def height(self) -> Union[int, float]:
        """
        Get the height of the size.

        :return: The height value.
        """
        return self._height

    def transposed(self) -> Size:
        return Size(self.height, self.width)
