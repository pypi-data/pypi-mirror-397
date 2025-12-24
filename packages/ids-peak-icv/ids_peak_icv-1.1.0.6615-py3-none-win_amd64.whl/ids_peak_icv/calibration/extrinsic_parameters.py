from __future__ import annotations

import ctypes
from typing import Any, cast
import numpy as np

from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_extrinsic_parameters, ctypes_objects_equal
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.exceptions import NotPossibleException
from ids_peak_icv.datatypes.geometry.point_xyz import PointXYZ


class ExtrinsicParameters:
    """
    Class for handling extrinsic parameters related to camera calibration.

    This class stores and provides access to the extrinsic parameters, which include
    the translation, rotation, and transformation matrix.
    
    It is a result of the camera calibration or the workspace calibration.  
    
    The extrinsic camera parameters describe the transformation between the camera's coordinate system and the world coordinate system.
    They can be used to convert points from the world coordinate system into the camera coordinate system.

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes an instance of ExtrinsicParameters.

        .. versionadded:: ids_peak_icv 1.1
        """

        try:
            self._parameters: peak_icv_extrinsic_parameters = kwargs["_parameters"]
        except KeyError:
            raise NotPossibleException("{} shall not be initialized directly".format(self.__class__.__name__))

        self._transformation_matrix: np.ndarray | None = None

    @property
    def translation(self) -> PointXYZ:
        """
        Returns the translation vector associated with the extrinsic parameters.

        :return: The translation as a numpy array (3D vector).

        .. versionadded:: ids_peak_icv 1.1
        """
        return PointXYZ(
            self._parameters.translation.x, self._parameters.translation.y, self._parameters.translation.z)

    @property
    def rotation(self) -> PointXYZ:
        """
        Returns the rotation vector (Rodrigues rotation) associated with the extrinsic parameters.

        :return: The rotation as a numpy array (3D vector).

        .. versionadded:: ids_peak_icv 1.1
        """
        return PointXYZ(self._parameters.rotation.x, self._parameters.rotation.y,
                        self._parameters.rotation.z)

    @property
    def transformation_matrix(self) -> np.ndarray:
        """
        Returns the transformation matrix calculated from the rotation and translation vectors.

        :return: A 4x4 transformation matrix.

        .. versionadded:: ids_peak_icv 1.1
        """

        if self._transformation_matrix is not None:
            return self._transformation_matrix

        self._transformation_matrix = np.zeros((4, 4), dtype=np.float32)

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Calibration_Extrinsic_CalculateTransformationMatrix,
            self._parameters, ctypes.sizeof(self._parameters),
            self._transformation_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))

        return cast(np.ndarray, self._transformation_matrix)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExtrinsicParameters):
            return False
        return ctypes_objects_equal(self._parameters, other._parameters)
