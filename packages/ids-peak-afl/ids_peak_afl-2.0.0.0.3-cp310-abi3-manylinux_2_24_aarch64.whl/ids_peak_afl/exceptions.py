import ids_peak_common.exceptions as common_exceptions


class Exception(common_exceptions.CommonException):
    """
    The class for most exceptions thrown by the library.
    """

    def __init__(self, error_description: str) -> None:
        super().__init__(error_description)


class InvalidParameterException(
    common_exceptions.InvalidParameterException, Exception
):
    """
    Thrown when a function receives an invalid parameter.

    Typically, indicates a null or otherwise invalid value
    passed to a parameter.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InternalErrorException(
    common_exceptions.InternalErrorException, Exception
):
    """
    Thrown when an unexpected internal error occurs.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidCastException(common_exceptions.InvalidCastException, Exception):
    """
    Thrown when a cast to an incompatible type is attempted.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class NotInitializedException(
    common_exceptions.LibraryNotInitializedException, Exception
):
    """
    Thrown when the library is used before proper initialization.

    Ensure that the library initialization function has been called
    before using other features.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class OutOfRangeException(common_exceptions.OutOfRangeException, Exception):
    """
    Thrown when a parameter is outside the valid range.

    Indicates a value that is either too high or too low for the
    expected bounds.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class TimeoutException(common_exceptions.TimeoutException, Exception):
    """
    Thrown when an operation exceeds its time limit.

    May indicate a hang, deadlock, or unresponsive resource.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class NotSupportedException(
    common_exceptions.NotSupportedException, Exception
):
    """
    Thrown when an unsupported operation or feature is used.

    Indicates functionality that is not available in the current context
    or platform.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BusyException(Exception):
    """
    Thrown for signaling a busy operation.

    .. note:: Try checking the status. If thrown by
              ``ids_peak_afl.ids_peak_afl.Manager``,
              call ``ids_peak_afl.ids_peak_afl.Manager.Status()`` first.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CorruptedDataException(Exception):
    """
    Thrown when a file could not be loaded because it is corrupted.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidImageFormatException(Exception):
    """
    Thrown for signaling an invalid image format.

    The provided image format is not supported by the auto feature algorithms
    or the format parameters are invalid.

    .. note:: Check supported pixel formats in the documentation
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BadAccessException(Exception):
    """
    Thrown for signaling an access error.

    The requested operation could not be performed due to insufficient
    permissions or the resource being locked by another process.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BufferTooSmallException(Exception):
    """
    Thrown when the supplied buffer is too small.

    The buffer provided for output data is smaller than required.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
