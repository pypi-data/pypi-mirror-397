from typing import Union, Any

from ids_peak_common import exceptions
from ids_peak_common._internal.utils import is_equal, validate_parameter_types


class Interval:
    """
    Represents an interval with lower and upper boundaries.

    .. ingroup:: ids_peak_common_python_types
    """

    def __init__(self, minimum: Union[int, float], maximum: Union[int, float]):
        """
        Creates an interval.

        :param minimum: The lower boundary.
        :param maximum: The upper boundary.

        :raises OutOfRangeException: If maximum is less than minimum.
        """
        validate_parameter_types(minimum, maximum, accepted_types=(int, float))
        if maximum < minimum:
            raise exceptions.OutOfRangeException(
                "Maximum value has to be bigger than or equal to the minimum value"
            )

        self._minimum = minimum
        self._maximum = maximum

    def __eq__(self, other: Any) -> bool:
        """
        Check if two intervals are equal.

        :param other: Another Interval object OR List of boundaries [minimum, maximum] OR Tuple of boundaries (minimum, maximum)

        :return: True if intervals are equal, False otherwise
        """
        if isinstance(other, Interval):
            return is_equal(self._minimum, other._minimum) and is_equal(self._maximum, other._maximum)
        if isinstance(other, (list, tuple)):
            if len(other) != 2:
                return False
            return is_equal(self._minimum, other[0]) and is_equal(self._maximum, other[1])
        return False

    def __ne__(self, other: Any) -> bool:
        """
        Check if two intervals are not equal.

        :param other: Another Interval object OR List of boundaries [minimum, maximum] OR Tuple of boundaries (minimum, maximum)

        :return: True if intervals are not equal, False otherwise
        """
        return not self.__eq__(other)

    def _is_negative(self) -> bool:
        return self._minimum < 0 or self._maximum < 0

    @property
    def minimum(self) -> Union[int, float]:
        """
        Returns the lower boundary of the interval.
        """
        return self._minimum

    @property
    def maximum(self) -> Union[int, float]:
        """
        Returns the upper boundary of the interval.
        """
        return self._maximum

    def __str__(self) -> str:
        """
        Returns a string representation of the Interval object.

        :return: String representation of the Interval object.
        """
        return f"(minimum={self.minimum}, maximum={self.maximum})"

    def __repr__(self) -> str:
        """
        Return an unambiguous string of the Interval object.
        """
        return f"{self.__class__.__name__}{str(self)}"
