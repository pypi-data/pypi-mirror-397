from typing import Union, Any

from ids_peak_common._internal.utils import is_equal, validate_parameter_types
from ids_peak_common.datatypes.interval import Interval
from ids_peak_common.exceptions import InvalidParameterException


class Range(Interval):
    """
    Represents a numeric range with defined boundaries and a fixed increment.

    A Range models a continuous sequence of values starting from a minimum value,
    ending at a maximum value, and progressing in steps defined by an increment.
    It supports integers and floating-point numbers.

    This class ensures that the increment does not exceed the total span between
    the minimum and maximum bounds. The range is inclusive of its boundary values.
    """

    def __init__(self, minimum: Union[int, float], maximum: Union[int, float], increment: Union[int, float]):
        """
        Creates a range with specified minimum, maximum, and increment values.

        :raises InvalidParameterException: If minimum is greater than maximum,
         or if increment exceeds the total range span.

        :param minimum: The inclusive starting (lower) boundary of the range.
        :param maximum: The inclusive ending (upper) boundary of the range.
        :param increment: The step size or increment between values within the range.
        """
        super().__init__(minimum, maximum)

        validate_parameter_types(minimum, maximum, increment, accepted_types=(int, float))

        if increment > self.maximum - self.minimum:
            raise InvalidParameterException("The given increment is larger than the total range!")
        self._increment = increment

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Range):
            return super().__eq__(other) and is_equal(other.increment, self.increment)
        if isinstance(other, list) or isinstance(other, tuple):
            if len(other) != 3:
                return False
            return super().__eq__((other[0], other[1])) and is_equal(self._increment, other[2])
        else:
            return False

    @property
    def increment(self) -> Union[int, float]:
        """
        Retrieves the increment value associated with this range.
        """
        return self._increment

    def __str__(self) -> str:
        """
        Returns a string representation of the Range object.

        :return: String representation of the Range object.
        """
        return f"(minimum={self.minimum}, maximum={self.maximum}, increment={self.increment})"

    def __repr__(self) -> str:
        """
        Return an unambiguous string of the Range object.
        """
        return f"{self.__class__.__name__}{str(self)}"