from typing import Any, Tuple, Type

from ids_peak_common.exceptions import InvalidParameterException


def is_equal(left: int | float, right: int | float, tolerance: float =1e-7) -> bool:
    """
    Compare two numbers for equality, allowing a tolerance for floating point comparison.

    :param left: First number (int or float).
    :param right: Second number (int or float).
    :param tolerance: Tolerance for floating point comparison. Ignored for integers.
    :return: True if the numbers are considered equal, False otherwise.
    """
    if isinstance(left, int) and isinstance(right, int):
        return left == right
    elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(left - right) < tolerance
    else:
        return False


def validate_parameter_types(*args: Any, accepted_types: Tuple[Type, ...]) -> None:
    """
    Validate that all given arguments are instances of the accepted types and are all of the same type.

    :param args: Parameters to validate.
    :param accepted_types: Tuple of allowed types (default: (int, float)).
    :raises TypeError: If any argument is not of an accepted type, or if the arguments have inconsistent types.
    """
    if not all(isinstance(v, accepted_types) for v in args):
        allowed = ", ".join(t.__name__ for t in accepted_types)
        raise InvalidParameterException(f"All parameters must be instances of: {allowed}")

    types = {type(v) for v in args}
    if len(types) > 1:
        raise InvalidParameterException("All parameters must be of the same type")
