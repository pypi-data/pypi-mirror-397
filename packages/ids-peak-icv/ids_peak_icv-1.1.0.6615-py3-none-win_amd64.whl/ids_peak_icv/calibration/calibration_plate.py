from __future__ import annotations

import ctypes
from typing import Any

from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_calibration_plate_handle
from ids_peak_icv.backend.utils import execute_and_map_return_codes, check_init_for_classes_with_classmethods_only


class CalibrationPlate:
    """
    Class for holding a calibration plate.

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    @classmethod
    def create_from_file(cls, file_path: str) -> CalibrationPlate:
        """
        Creates an instance of CalibrationPlate by loading the calibration plate from a file.

        For a camera calibration a calibration plate is needed.

        :param file_path: An existing file path to a JSON file containing the calibration plate.

        :raises IOException: If the given file_path does not exist, or the permissions are not sufficient
        to read it.
        :raises CorruptedException: If the file content is corrupted.
        :return: A new instance of CalibrationPlate

        .. versionadded:: ids_peak_icv 1.1
        """
        c_file_path = file_path.encode('utf-8')

        handle = peak_icv_calibration_plate_handle()

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Plate_CreateFromFile,
                                     ctypes.pointer(handle),
                                     ctypes.c_char_p(c_file_path),
                                     ctypes.c_size_t(len(c_file_path)))
        return cls(_handle=handle)

    @classmethod
    def _create_empty(cls) -> CalibrationPlate:
        handle = peak_icv_calibration_plate_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Plate_Create,
                                     ctypes.pointer(handle))

        return CalibrationPlate(_handle=handle)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create a CalibrationPlate, please refer to the classmethods.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._handle = check_init_for_classes_with_classmethods_only(self.__class__.__name__,
                                                                     peak_icv_calibration_plate_handle,
                                                                     *args, **kwargs)

    def __del__(self) -> None:
        if hasattr(self, '_handle'):
            lib_loader.dll().peak_icv_Calibration_Plate_Destroy(self._handle)
