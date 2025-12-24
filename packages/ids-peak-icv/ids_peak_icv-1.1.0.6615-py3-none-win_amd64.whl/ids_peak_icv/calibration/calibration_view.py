from __future__ import annotations

import ctypes
from typing import TypeAlias, Any, cast

import numpy as np
import numpy.typing as npt

from ids_peak_common.datatypes.geometry.point import Point, Vector
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import (peak_icv_reprojection_error, peak_icv_calibration_view_handle,
                                              peak_icv_extrinsic_parameters, peak_icv_coordinate_system)
from ids_peak_icv.backend.utils import execute_and_map_return_codes, create_array
from ids_peak_icv.exceptions import NotPossibleException
from ids_peak_icv.calibration.extrinsic_parameters import ExtrinsicParameters
from ids_peak_icv.calibration.reprojection_error import ReprojectionError
from ids_peak_icv.datatypes.geometry.coordinate_system import CoordinateSystem
from ids_peak_icv.datatypes.geometry.polygon import Polygon

# Note: We loose type info here, as it is stored as a pointer to a python object
ReprojectionErrorArray: TypeAlias = npt.NDArray[np.object_]


class CalibrationView:
    """
    Class for holding the extrinsic result for one image of a camera calibration and also the reprojection
    errors of every detected marker.

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    @classmethod
    def _create_empty(cls) -> CalibrationView:
        handle = peak_icv_calibration_view_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_Create,
                                     ctypes.pointer(handle))

        return CalibrationView(_handle=handle)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Please do not use this function. Refer to CalibrationResult.views to get views from a calibration result.

        .. versionadded:: ids_peak_icv 1.1
        """
        try:
            self._handle = kwargs["_handle"]
        except KeyError:
            raise NotPossibleException("{} shall not be initialized".format(self.__class__.__name__))
        self._errors: np.ndarray | None = None

    def __del__(self) -> None:
        if hasattr(self, '_handle'):
            lib_loader.dll().peak_icv_Calibration_View_Destroy(self._handle)

    @property
    def mean_reprojection_error(self) -> float:
        """
        Provides the mean reprojection error from a calibration view.

        The reprojection error is the distance between the marker points extracted from the calibration
        images and the projected world points from CalibrationPlateInfo.

        :return: Returns the mean reprojection error.

        .. versionadded:: ids_peak_icv 1.1
        """
        mean_reprojection_error = ctypes.c_double()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_GetMeanReprojectionError,
                                     self._handle,
                                     ctypes.pointer(mean_reprojection_error))
        return mean_reprojection_error.value

    @property
    def maximum_reprojection_error(self) -> float:
        """
        Provides the maximum reprojection error from a calibration view.

        The reprojection error is the distance between the marker points extracted from the calibration
        images and the projected world points from CalibrationPlateInfo.

        :return: Returns the maximum reprojection error.

        .. versionadded:: ids_peak_icv 1.1
        """
        maximum_reprojection_error = ctypes.c_double()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_GetMaximumReprojectionError,
                                     self._handle,
                                     ctypes.pointer(maximum_reprojection_error))
        return maximum_reprojection_error.value

    @property
    def reprojection_errors(self) -> ReprojectionErrorArray:
        """
        Provides the reprojection errors for every marker in the view.

        The reprojection error is the distance between the marker points extracted from the calibration images and
        the projected world points from CalibrationPlateInfo.

        :return: Returns all reprojection errors.

        .. versionadded:: ids_peak_icv 1.1
        """
        if self._errors is not None:
            return self._errors

        num_reprojection_errors = ctypes.c_size_t()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_GetReprojectionErrors_GetCount,
                                     self._handle,
                                     ctypes.pointer(num_reprojection_errors))

        if num_reprojection_errors.value == 0:
            self._errors = np.array([])
            return cast(ReprojectionErrorArray, self._errors)

        errors = create_array(peak_icv_reprojection_error, num_reprojection_errors.value)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_GetReprojectionErrors, self._handle,
                                     ctypes.pointer(errors), num_reprojection_errors)

        # workaround to fill the array on python3.7 with numpy
        self._errors = np.empty(len(errors), dtype=ReprojectionError)
        for i, it in enumerate(errors):
            self._errors[i] = ReprojectionError(Point(it.position.x, it.position.y),
                                                Vector(it.direction.x, it.direction.y), it.length)

        return cast(ReprojectionErrorArray, self._errors)

    @property
    def extrinsic_parameters(self) -> ExtrinsicParameters:
        """
        Provides the extrinsic parameters for the view.

        A view always contains extrinsic parameters that describe the transformation from the calibration plate coordinate
        system into the camera coordinate system.

        :return: Returns the extrinsic parameters from a calibration view.

        .. versionadded:: ids_peak_icv 1.1
        """
        extrinsic_parameters = peak_icv_extrinsic_parameters()

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_GetExtrinsicParameters,
                                     self._handle,
                                     ctypes.pointer(extrinsic_parameters), ctypes.sizeof(extrinsic_parameters))

        return ExtrinsicParameters(_parameters=extrinsic_parameters)

    @property
    def convex_hull(self) -> Polygon:
        """
        Provides the convex hull of the found calibration pattern in the view.

        :return: Returns the convex hull as polygon from a calibration view.

        .. versionadded:: ids_peak_icv 1.1
        """
        polygon = Polygon()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_GetConvexHull,
                                     self._handle,
                                     ctypes.pointer(polygon._handle))

        return polygon

    @property
    def coordinate_system(self) -> CoordinateSystem:
        """
        Provides the coordinate system of the calibration view that was projected into the image plane.
        The coordinate system is represented by its origin and three vectors, each corresponding to one of the three coordinate axes (X, Y and
        Z). These vectors describe the directions of the respective axes projected from 3D into 2D space. Their lengths are determined by twice
        the distance between neighboring markers on the calibration plate.

        :return: Returns the coordinate system from a calibration view.

        .. versionadded:: ids_peak_icv 1.1
        """
        coordinate_system = peak_icv_coordinate_system()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_View_GetCoordinateSystem,
                                     self._handle,
                                     ctypes.pointer(coordinate_system))

        return CoordinateSystem(Point(coordinate_system.origin.x, coordinate_system.origin.y),
                                Point(coordinate_system.x_axis.x, coordinate_system.x_axis.y),
                                Point(coordinate_system.y_axis.x, coordinate_system.y_axis.y),
                                Point(coordinate_system.z_axis.x, coordinate_system.z_axis.y))
