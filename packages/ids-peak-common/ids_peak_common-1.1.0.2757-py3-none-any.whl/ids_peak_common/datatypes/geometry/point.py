from typing import Union, Any

from ids_peak_common._internal.utils import is_equal, validate_parameter_types


class Point:
    """
    Represents a point in 2D space with x and y coordinates.

    .. ingroup:: ids_peak_common_python_types_geometry
    """

    def __init__(self, x: Union[int, float], y: Union[int, float]):
        """
        Initializes a Point instance.

        :param x: x coordinate
        :param y: y coordinate
        """
        validate_parameter_types(x, y, accepted_types=(int, float))
        self._x: Union[int, float] = x
        self._y: Union[int, float] = y

    def __eq__(self, other: Any) -> bool:
        """
        Determines if this point is equal to another point or coordinate pair.

        :param other: Another Point object OR List of coordinates [x,y] OR Tuple of coordinates (x,y)

        :return: True if points are equal, False otherwise
        """
        if isinstance(other, Point):
            return is_equal(self.x, other.x) and is_equal(self.y, other.y)
        if isinstance(other, (list, tuple)):
            if len(other) != 2:
                return False
            return is_equal(self.x, other[0]) and is_equal(self.y, other[1])
        return False

    def __ne__(self, other: Any) -> bool:
        """
        Determines if this point is not equal to another point or coordinate pair.

        :param other: Another Point instance, or a list/tuple with two numeric elements [x, y] or (x, y).

        :return: True if points are not equal, False otherwise
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        """
        Returns a string representation of the Point.

        A string in the format "(x: <x_value>, y: <y_value>)".
        """
        return f"(x={self.x}, y={self.y})"

    def __repr__(self) -> str:
        """
        Return an unambiguous string of the Point object.
        """
        return f"{self.__class__.__name__}{str(self)}"

    @property
    def x(self) -> Union[int, float]:
        return self._x

    @property
    def y(self) -> Union[int, float]:
        return self._y


Vector = Point
