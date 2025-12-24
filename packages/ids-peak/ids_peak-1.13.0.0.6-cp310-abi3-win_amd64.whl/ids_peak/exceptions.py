from ids_peak_common import exceptions


class Exception(exceptions.CommonException):
    """
    The base class for all exceptions thrown by the library.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class AbortedException(Exception):
    """
    The exception thrown for signaling an aborted operation.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class BadAccessException(Exception):
    """
    The exception thrown for signaling an access error.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class BadAllocException(exceptions.BadAllocException, Exception):
    """
    The exception thrown for signaling a failed memory allocation.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class InternalErrorException(exceptions.InternalErrorException, Exception):
    """
    The exception thrown for internal errors.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class InvalidAddressException(Exception):
    """
    The exception thrown for trying to work on an invalid address.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class InvalidArgumentException(exceptions.InvalidParameterException, Exception):
    """
    The exception thrown for passing an invalid argument to a function.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class InvalidCastException(exceptions.InvalidCastException, Exception):
    """
    The exception thrown for trying to apply an invalid cast.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class InvalidInstanceException(Exception):
    """
    The exception thrown for trying to work on an invalid instance.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class NotAvailableException(Exception):
    """
    The exception thrown for signaling that a feature is not available in the device.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class NotFoundException(Exception):
    """
    The exception thrown for signaling a failed find operation.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class NotImplementedException(Exception):
    """
    The exception thrown for signaling a feature is not implemented.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class NotInitializedException(exceptions.LibraryNotInitializedException, Exception):
    """
    The exception thrown for signaling that the library was not initialized.

    Notes: Remember to call Initialize() / PEAK_Library_Initialize() before anything else.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class OutOfRangeException(exceptions.OutOfRangeException, Exception):
    """
    The exception thrown for trying to access a value that is out of range.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class TimeoutException(exceptions.TimeoutException, Exception):
    """
    The exception thrown for signaling an exceeded timeout during a function call.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class IOException(exceptions.IOException, Exception):
    """
    The exception thrown for a communication error.

    A communication error has occured. Most likely due to the device being
    disconnected.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class NoDataException(Exception):
    """
    The exception thrown for signalling that the requested data is not available.

    The requested data or information is not available.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)


class CTILoadingException(Exception):
    """
    The exception thrown for signaling an error on opening a cti.
    """

    def __init__(self, error_description: str):
        super().__init__(error_description)
