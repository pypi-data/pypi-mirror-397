from __future__ import annotations

import ctypes
from typing import TypeAlias, Any

import numpy as np
import numpy.typing as npt

from ids_peak_icv import lib_loader
from ids_peak_icv.exceptions import ICVException
from ids_peak_icv.backend.datatypes import (peak_icv_calibration_result_handle, peak_icv_calibration_view_handle,
                                              peak_icv_calibration_parameters)
from ids_peak_icv.backend.utils import (execute_and_map_return_codes, create_array,
                                          check_init_for_classes_with_classmethods_only)
from ids_peak_icv.calibration.calibration_parameters import CalibrationParameters
from ids_peak_icv.calibration.calibration_view import CalibrationView

# Note: We loose type info here, as it is stored as a pointer to a python object
CalibrationViewArray: TypeAlias = npt.NDArray[np.object_]


class CalibrationResult:
    """
    Class for holding the results of a camera calibration.

    The CalibrationResult stores intrinsic and extrinsic parameters as well as the
    mean reprojection error calculated by CameraCalibration.process().

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    @classmethod
    def create_from_file(cls, file_path: str) -> CalibrationResult:
        """
        Creates an instance of CalibrationResult by loading the calibration result from a file.

        :param file_path: An existing file path to a JSON file containing the calibration result.
        :return: A new instance of CalibrationResult

        :raises IOException: If the given file_path does not exist, or the permissions are not sufficient
                             to read it.
        :raises CorruptedException: If the file content is corrupted.

        .. versionadded:: ids_peak_icv 1.1
        """
        c_file_path = file_path.encode('utf-8')

        handle = peak_icv_calibration_result_handle()

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Result_CreateFromFile,
                                     ctypes.pointer(handle),
                                     ctypes.c_char_p(c_file_path),
                                     ctypes.c_size_t(len(c_file_path)))
        return cls(_handle=handle)

    @classmethod
    def _create_empty(cls) -> CalibrationResult:
        handle = peak_icv_calibration_result_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Result_Create,
                                     ctypes.pointer(handle))

        return CalibrationResult(_handle=handle)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create a CalibrationResult, please refer to the classmethods.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._handle = check_init_for_classes_with_classmethods_only(self.__class__.__name__,
                                                                     peak_icv_calibration_result_handle,
                                                                     *args, **kwargs)
        self._views: np.ndarray | None = None

    def __del__(self) -> None:
        if hasattr(self, '_handle'):
            lib_loader.dll().peak_icv_Calibration_Result_Destroy(self._handle)

    @property
    def mean_reprojection_error(self) -> float:
        """
        Provides the mean reprojection error from calibration result.

        The mean reprojection error is the root-mean-square of distances between the marker points extracted from the
        calibration images and the projected world points from the used calibration plate.

        .. versionadded:: ids_peak_icv 1.1
        """
        c_mean_reprojection_error = ctypes.c_double()

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Result_GetMeanReprojectionError,
                                     self._handle, ctypes.pointer(c_mean_reprojection_error))
        return c_mean_reprojection_error.value

    @property
    def views(self) -> CalibrationViewArray:
        """
        Provides a list of ``CalibrationView``.

        The order in which the CalibrationViews are provided, is equivalent to the order of images provided to
        CameraCalibration.CameraCalibration.Process.

        .. versionadded:: ids_peak_icv 1.1
        """
        if self._views is not None:
            return self._views

        view_count = ctypes.c_size_t()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Result_GetCalibrationViews_GetCount,
                                     self._handle, ctypes.pointer(view_count))

        if view_count.value == 0:
            # note: this is needed as doxygen reports something about npt NDArray not being defined
            # @cond HIDE_FROM_DOXYGEN
            self._views = np.array([])
            # @endcond
            return self._views

        view_handles = create_array(peak_icv_calibration_view_handle, view_count.value)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_Array_Create,
                                     view_handles, view_count)
        try:
            execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Result_GetCalibrationViews,
                                         self._handle, view_handles, view_count)
            views = np.array([CalibrationView(_handle=h) for h in view_handles])
        except ICVException as e:
            lib_loader.dll().peak_icv_Calibration_View_Array_Destroy(view_handles, view_count)
            raise e

        self._views = views
        return self._views

    def save(self, file_path: str) -> None:
        """
        Saves calibration result to a JSON file for later use.

        :param file_path: An existing file path to save calibration result.

        :raises IOException: If the specified file path is invalid, you lack the necessary permissions, or
         the file already exists.

        .. versionadded:: ids_peak_icv 1.1
        """
        c_file_path = file_path.encode('utf-8')
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Result_SaveToFile,
                                     self._handle,
                                     ctypes.c_char_p(c_file_path))

    @property
    def calibration_parameters(self) -> CalibrationParameters:
        """
        Provides the @p CalibrationParameters that contain the necessary information to use the camera calibration.

        :return: An instance of CalibrationParameters

        .. versionadded:: ids_peak_icv 1.1
        """
        parameters = peak_icv_calibration_parameters()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Result_ToParameters,
                                     self._handle, ctypes.pointer(parameters), ctypes.sizeof(parameters))

        return CalibrationParameters(_parameters=parameters)
