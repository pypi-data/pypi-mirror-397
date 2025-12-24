from __future__ import annotations

from typing import Union, Any

from ids_peak_common._internal.utils import validate_parameter_types
from ids_peak_common.datatypes.geometry.point import Point
from ids_peak_common.datatypes.geometry.size import Size


class Rectangle:
    """
    A rectangle defined by a point and a size.

    Represents a rectangle composed of a position (top-left corner) and a size.
    The position and size types are customizable via template parameters.

    .. ingroup:: ids_peak_common_python_types_geometry
    """

    def __init__(self, point: Point, size: Size) -> None:
        """
        Creates a rectangle from a point and a size.
        :param point: The top-left corner of the rectangle.
        :param size: The dimensions of the rectangle.
        """

        if isinstance(point, Point) and isinstance(size, Size):
            validate_parameter_types(
                point.x, point.y, size.width, size.height,
                accepted_types=(int, float))
            self._point: Point = point
            self._size: Size = size
        else:
            raise TypeError("Rectangle expected (Point, Size)")

    @classmethod
    def create_from_coordinates_and_dimensions(
        cls,
        x: Union[int, float],
        y: Union[int, float],
        width: Union[int, float],
        height: Union[int, float]
    ) -> Rectangle:
        """
        Constructs a rectangle from x, y, width and height.
        :param x: x coordinate of the upper left corner
        :param y: y coordinate of the upper left corner
        :param width: Width of the rectangle
        :param height: Height of the rectangle
        """
        validate_parameter_types(x, y, width, height,
                                 accepted_types=(int, float))
        return Rectangle(Point(x, y), Size(width, height))

    def __eq__(self, other: Any) -> bool:
        """
        Check if two rectangles are equal.

        :param other: Another rectangle object OR
                      List of coordinates [x,y,width,height] OR
                      Tuple of coordinates (x,y,width,height)

        :return: True if rectangles are equal, False otherwise
        """
        if isinstance(other, Rectangle):
            return self._point == other.position and self._size == other.size
        if isinstance(other, (list, tuple)):
            if len(other) != 4:
                return False
            return Point.__eq__(self._point, other[:2]) and Size.__eq__(self._size, other[2:])

        return False

    def __ne__(self, other: Any) -> bool:
        """
        Check if two rectangles are not equal.

        :param other: Another rectangle object

        :return: True if rectangles are not equal, False otherwise
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        """
        Get a string representation of the rectangle.

        :return: String representation of the rectangle
        """
        return (f"(x={self.x}, y={self.y}, width={self.width}, "
                f"height={self.height})")

    def __repr__(self) -> str:
        """
        Return an unambiguous string of the Rectangle object.
        """
        return (f"{self.__class__.__name__}(point={self._point!r}, "
                f"size={self._size!r})")

    @property
    def position(self) -> Point:
        """
        Returns the top-left corner of the rectangle.
        """
        return self._point

    @property
    def size(self) -> Size:
        """
        Returns the dimensions of the rectangle.
        """
        return self._size

    @property
    def x(self) -> Union[int, float]:
        """
        Returns the x-coordinate of the rectangle's top-left corner.
        """
        return self._point.x

    @property
    def y(self) -> Union[int, float]:
        """
        Returns the y-coordinate of the rectangle's top-left corner.
        """
        return self._point.y

    @property
    def width(self) -> Union[int, float]:
        """
        Returns the width of the rectangle.
        """
        return self._size.width

    @property
    def height(self) -> Union[int, float]:
        """
        Returns the height of the rectangle.
        """
        return self._size.height
