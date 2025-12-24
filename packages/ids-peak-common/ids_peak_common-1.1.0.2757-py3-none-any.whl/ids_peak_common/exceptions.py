class CommonException(Exception):
    """
    Base class for all exceptions thrown by the library.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class InvalidParameterException(CommonException):
    """
    Thrown when a function receives an invalid parameter.

    Typically, indicates a null or otherwise invalid value passed to a parameter.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class BadAllocException(CommonException):
    """
    Thrown when memory allocation fails.

    Indicates that the system was unable to allocate the required memory.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class InternalErrorException(CommonException):
    """
    Thrown when an unexpected internal error occurs.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class InvalidCastException(CommonException):
    """
    Thrown when a cast to an incompatible type is attempted.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class LibraryNotInitializedException(CommonException):
    """
    Thrown when the library is used before proper initialization.

    Ensure that the library initialization function has been called before using other features.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class OutOfRangeException(CommonException):
    """
    Thrown when a parameter is outside the valid range.

    Indicates a value that is either too high or too low for the expected bounds.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class TimeoutException(CommonException):
    """
    Thrown when an operation exceeds its time limit.

    May indicate a hang, deadlock, or unresponsive resource.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class IOException(CommonException):
    """
    Thrown when an input, output, file or device communication error occurs.

    Often indicates a disconnection or failure to access a hardware device or file.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)


class NotSupportedException(CommonException):
    """
    Thrown when an unsupported operation or feature is used.

    Indicates functionality that is not available in the current context or platform.

    .. ingroup:: ids_peak_common_python_exceptions
    """

    def __init__(self, message: str):
        super().__init__(message)
