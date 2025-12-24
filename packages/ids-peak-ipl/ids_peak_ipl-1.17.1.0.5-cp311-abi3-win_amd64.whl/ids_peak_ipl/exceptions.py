import ids_peak_common.exceptions


class Exception(ids_peak_common.exceptions.CommonException):
    """
    The base class for all exceptions thrown by the library.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)



class OutOfRangeException(ids_peak_common.exceptions.OutOfRangeException, Exception):
    """
    The exception thrown for trying to access a value being out of range.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class BufferTooSmallException(Exception):
    """
    The exception thrown when a given buffer is too small for the data.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class InvalidArgumentException(ids_peak_common.exceptions.InvalidParameterException, Exception):
    """
    The exception thrown when passing an invalid parameter to a function.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class ImageFormatNotSupportedException(ids_peak_common.exceptions.NotSupportedException, Exception):
    """
    The exception thrown when an image format isn't supported by a function.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class ImageFormatInterpretationException(Exception):
    """
    The exception thrown when a given image format can't be used on this data, e.g. during reading from file.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class IOException(ids_peak_common.exceptions.IOException, Exception):
    """
    The exception thrown when a given image format can't be used on this data, e.g. during reading from file.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class BusyException(Exception):
    """
    The exception thrown when the resource busy.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class NotPermittedException(Exception):
    """
    The exception thrown when the operation not permitted.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class TimeoutException(ids_peak_common.exceptions.TimeoutException, Exception):
    """
    The exception thrown when the operation times out.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)


class InvalidHandleException(Exception):
    """
    The exception thrown when passing an invalid handle to a function.
    """
    def __init__(self, error_description: str):
        super().__init__(error_description)
