from __future__ import annotations
import atexit
import ctypes
import os
import site
import sys
from typing import Callable, Type, TypeVar, Sequence, Any, MutableSequence, Union

from ids_peak_common import Metadata, MetadataKey, Rectangle, Point, Size
from ids_peak_icv.backend.datatypes import (peak_icv_status, peak_icv_point_f, peak_icv_point_type,
                                              peak_icv_capture_information)
from ids_peak_icv.exceptions import (InvalidConfigurationException, MismatchException, NotSupportedException,
                                       NotPossibleException, OutOfRangeException, MathErrorException,
                                       TargetNotFoundException, CorruptedException, IOException, InternalErrorException,
                                       ICVException, NullPointerException)
from numpy.typing import NDArray


def create_array(c_type: Any, size: int) -> ctypes.Array:
    array_class: Type[ctypes.Array] = c_type * size
    return array_class()


def metadata_to_capture_information(metadata: Metadata, size: Size | None = None) -> peak_icv_capture_information:
    c_capture_information = peak_icv_capture_information()

    if metadata.has_entry_by_key(MetadataKey.DEVICE_TIMESTAMP):
        c_capture_information.relative_timestamp = metadata.get_value_by_key(MetadataKey.DEVICE_TIMESTAMP)
    else:
        c_capture_information.relative_timestamp = 0
    if metadata.has_entry_by_key(MetadataKey.BINNING_HORIZONTAL):
        c_capture_information.binning_factor.x = metadata.get_value_by_key(MetadataKey.BINNING_HORIZONTAL)
    else:
        c_capture_information.binning_factor.x = 1
    if metadata.has_entry_by_key(MetadataKey.BINNING_VERTICAL):
        c_capture_information.binning_factor.y = metadata.get_value_by_key(MetadataKey.BINNING_VERTICAL)
    else:
        c_capture_information.binning_factor.y = 1
    if metadata.has_entry_by_key(MetadataKey.ROI):
        roi = metadata.get_value_by_key(MetadataKey.ROI)
        c_capture_information.region_of_interest.x = ctypes.c_uint32(roi.x)
        c_capture_information.region_of_interest.y = ctypes.c_uint32(roi.y)
        c_capture_information.region_of_interest.width = ctypes.c_uint32(roi.width)
        c_capture_information.region_of_interest.height = ctypes.c_uint32(roi.height)
    else:
        c_capture_information.region_of_interest.x = 0
        c_capture_information.region_of_interest.y = 0

        if size is not None:
            c_capture_information.region_of_interest.width = size.width
            c_capture_information.region_of_interest.height = size.height
        else:
            c_capture_information.region_of_interest.width = 0
            c_capture_information.region_of_interest.height = 0

    return c_capture_information


def metadata_from_capture_information(capture_information: peak_icv_capture_information) -> Metadata:
    metadata = Metadata()
    metadata.set_value_by_key(MetadataKey.DEVICE_TIMESTAMP, capture_information.relative_timestamp)
    metadata.set_value_by_key(MetadataKey.BINNING_HORIZONTAL, capture_information.binning_factor.x)
    metadata.set_value_by_key(MetadataKey.BINNING_VERTICAL, capture_information.binning_factor.y)
    metadata.set_value_by_key(MetadataKey.ROI, Rectangle(Point(capture_information.region_of_interest.x,
                                                               capture_information.region_of_interest.y),
                                                         Size(capture_information.region_of_interest.width,
                                                              capture_information.region_of_interest.height)))
    return metadata


def image_handle_to_ctypes(image_handle: int) -> ctypes.c_void_p:
    return ctypes.c_void_p(int(image_handle))


def map_point_type_to_native_type(point_type: Type) -> Type:
    if point_type == peak_icv_point_f:
        return float

    raise NotSupportedException(
        "Point type not supported.")


def map_point_type_to_enum(point_type: Type) -> peak_icv_point_type:
    if point_type == peak_icv_point_f:
        return peak_icv_point_type.PEAK_ICV_POINT_TYPE_XY

    raise NotSupportedException(
        "Point type not supported.")


def map_enum_to_point_type(point_enum: peak_icv_point_type) -> Type:
    if point_enum == peak_icv_point_type.PEAK_ICV_POINT_TYPE_XY:
        return peak_icv_point_f

    raise NotSupportedException(
        "point_enum not supported " + str(point_enum.value))


T = TypeVar('T', bound=Any)
InputType = Union[Sequence[T], NDArray[T], ctypes.Array[Any]]
OutputType = Union[MutableSequence[T], NDArray[T], ctypes.Array[Any]]


def transform(input_: InputType, output: OutputType, func: Callable) -> None:
    for i in range(len(input_)):
        output[i] = func(input_[i])


def execute_and_map_return_codes(func: Callable, *args: Any, **kwargs: Any) -> None:
    def execute_and_map_return_codes_light(func_light: Callable, *args_light: Any, **kwargs_light: Any) -> None:
        ec = func_light(*args_light, **kwargs_light)
        ec = peak_icv_status(ec)

        if ec != peak_icv_status.PEAK_ICV_STATUS_SUCCESS:
            raise ICVException("Could not query the last error!", ec)

    error_code = func(*args, **kwargs)

    try:
        error_code = peak_icv_status(error_code)
    except ValueError:
        # ignore key error here and throw the exception later, which then contains the error message
        pass

    if error_code != peak_icv_status.PEAK_ICV_STATUS_SUCCESS:

        c_count = ctypes.c_size_t()
        execute_and_map_return_codes_light(
            Loader().dll().peak_icv_GetLastErrorMessage_GetCount,
            ctypes.pointer(c_count))

        if c_count.value == 0:
            exception_msg = ""
        else:
            c_array = create_array(ctypes.c_char, c_count.value)
            execute_and_map_return_codes_light(Loader().dll().peak_icv_GetLastErrorMessage,
                                               c_array, c_count)
            exception_msg = c_array.value

        if error_code in {
            peak_icv_status.PEAK_ICV_STATUS_LIBRARY_NOT_INITIALIZED,
            peak_icv_status.PEAK_ICV_STATUS_DYNAMIC_DEPENDENCY_MISSING,
        }:
            raise InvalidConfigurationException(exception_msg, error_code)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_NULL_POINTER:
            raise NullPointerException(exception_msg)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_MISMATCH:
            raise MismatchException(exception_msg)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_NOT_SUPPORTED:
            raise NotSupportedException(exception_msg)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_NOT_POSSIBLE:
            raise NotPossibleException(exception_msg)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_OUT_OF_RANGE:
            raise OutOfRangeException(exception_msg)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_MATH_ERROR:
            raise MathErrorException(exception_msg)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_TARGET_NOT_FOUND:
            raise TargetNotFoundException(exception_msg)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_CORRUPTED:
            raise CorruptedException(exception_msg)

        elif error_code == peak_icv_status.PEAK_ICV_STATUS_IO_ERROR:
            raise IOException(exception_msg)

        elif error_code in {
            peak_icv_status.PEAK_ICV_STATUS_INTERNAL_ERROR,
            peak_icv_status.PEAK_ICV_STATUS_INVALID_BUFFER_SIZE,
            peak_icv_status.PEAK_ICV_STATUS_INVALID_HANDLE,
        }:
            raise InternalErrorException(exception_msg)
        else:
            raise ICVException(exception_msg, error_code)


def find_ids_peak_ipl_dll() -> str:
    for path in site.getsitepackages():
        package_path = os.path.join(path, "ids_peak_ipl")
        if os.path.isdir(package_path):
            return package_path
    raise InvalidConfigurationException("ids_peak_ipl.dll not found.",
                                        peak_icv_status.PEAK_ICV_STATUS_DYNAMIC_DEPENDENCY_MISSING)


class Loader:
    _instance = None
    _dll: ctypes.CDLL | None = None

    def __new__(cls) -> Loader:
        if cls._instance is None:
            cls._instance = super(Loader, cls).__new__(cls)
            file_dir = os.path.dirname(os.path.realpath(__file__))

            if sys.platform.startswith('win'):
                lib_name = "ids_peak_icv.dll"
                dll_path = os.path.join(file_dir, "..")
                os.add_dll_directory(dll_path)
                ids_peak_ipl_dll_path = find_ids_peak_ipl_dll()
                os.add_dll_directory(ids_peak_ipl_dll_path)
            else:
                lib_name = "libids_peak_icv.so"

            lib_path = os.path.abspath(os.path.join(file_dir, "..", lib_name))

            cls._instance._dll = ctypes.cdll.LoadLibrary(lib_path)

            execute_and_map_return_codes(cls._instance._dll.peak_icv_Init)

            atexit.register(Loader._library_exit)

        return cls._instance

    def dll(self) -> ctypes.CDLL:
        if self._dll is None:
            raise NotPossibleException("DLL is not loaded")
        return self._dll

    # https://docs.python.org/3/reference/datamodel.html From Python Docs: It is not guaranteed that __del__() methods
    # are called for objects that still exist when the interpreter exits.
    @staticmethod
    def _library_exit() -> None:
        execute_and_map_return_codes(Loader().dll().peak_icv_Exit)


ReturnType = TypeVar('ReturnType', bound=ctypes.c_void_p)


def check_init_for_classes_with_classmethods_only(class_name: str, return_type: Type[ReturnType],
                                                  *args: Any, **kwargs: Any) -> ReturnType:
    try:
        handle = kwargs["_handle"]
        if type(handle) is not return_type:
            raise NotPossibleException(f"Invalid handle type {type(handle)} found.")

        return handle
    except KeyError:
        raise NotPossibleException(
            f"Cannot initialize {class_name} with __init__. Please use a classmethod.")
