import ids_peak_common.exceptions
from ids_peak_icv.backend.datatypes import peak_icv_status


class ICVException(ids_peak_common.exceptions.CommonException):
    """
    Base class for all exceptions thrown by the IDS peak ICV library.

    :param message: Exception message.
    :param status: peak_icv_status associated with the exception.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str, status: peak_icv_status):
        super().__init__(message)
        self.status = status


class InvalidConfigurationException(ICVException):
    """
    Thrown when the library configuration is invalid.

    This can occur if a required dependency is missing, the library is not initialized,
    or other misconfiguration issues arise.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str, status: peak_icv_status):
        super().__init__(message, status)


class InternalErrorException(
    ICVException,
    ids_peak_common.exceptions.InternalErrorException
):
    """
    Thrown on unexpected internal system errors.

    Occurs when a failure happens during processing due to an unhandled condition
    in the routine.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_INTERNAL_ERROR)


class MismatchException(ICVException):
    """
    Thrown when input parameters do not match the expected conditions.

    For example, this occurs when two input images have different sizes but identical sizes are required.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_MISMATCH)


class NotSupportedException(
    ICVException,
    ids_peak_common.exceptions.NotSupportedException
):
    """
    Thrown when a requested operation is not implemented or supported.

    This occurs, for example, when trying to export to an unsupported file format.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_NOT_SUPPORTED)


class NotPossibleException(ICVException):
    """
    Thrown when an operation cannot be performed due to logical constraints.

    For example, this occurs when attempting camera calibration without any input images.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_NOT_POSSIBLE)


class OutOfRangeException(
    ICVException,
    ids_peak_common.exceptions.OutOfRangeException
):
    """
    Thrown when a value is outside the allowed range.

    This occurs, for example, when setting opacity to 101 although the valid range is 0–100.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_OUT_OF_RANGE)


class MathErrorException(ICVException):
    """
    Thrown when a mathematical computation fails.

    This occurs, for example, in cases such as division by zero or invalid operations in matrix computations.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_MATH_ERROR)


class TargetNotFoundException(ICVException):
    """
    Thrown when an expected target object is not detected in the input image.

    This occurs, for example, when a calibration plate or marker is missing or not detected in an input image.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_TARGET_NOT_FOUND)


class CorruptedException(ICVException):
    """
    Thrown when input data or a file is malformed, unreadable, or otherwise corrupted.

    This occurs when reading from a file or stream that is incomplete, damaged, or in an unexpected format.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_CORRUPTED)


class IOException(
    ICVException,
    ids_peak_common.exceptions.IOException
):
    """
    Thrown when a file input/output operation fails.

    This can occur due to reasons such as a missing file, insufficient permissions, or an inaccessible directory.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_IO_ERROR)


class NullPointerException(ICVException):
    """
    Thrown when attempting to access an object or value that has not been initialized.

    Indicates usage of a null pointer.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self, message: str):
        super().__init__(message, peak_icv_status.PEAK_ICV_STATUS_NULL_POINTER)
