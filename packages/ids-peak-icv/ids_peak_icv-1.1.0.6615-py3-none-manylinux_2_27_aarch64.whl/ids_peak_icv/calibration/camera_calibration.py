# @package CameraCalibration

from __future__ import annotations

import ctypes
from typing import TypeAlias, Any

import numpy as np
import numpy.typing as npt

from ids_peak_icv import lib_loader
from ids_peak_icv.exceptions import NotSupportedException, NotPossibleException
from ids_peak_icv.calibration.calibration_result import CalibrationResult
from ids_peak_icv.calibration.calibration_plate import CalibrationPlate
from ids_peak_icv.backend.datatypes import peak_icv_calibration_result_handle
from ids_peak_icv.backend.utils import execute_and_map_return_codes, create_array, transform

from ids_peak_icv.datatypes.image import _check_and_get_icv_image

# Note: We loose type info here, as it is stored as a pointer to a python object
ImageArray: TypeAlias = npt.NDArray[np.object_]


class CameraCalibration:
    """
    Class for calibrating a camera.

    The CameraCalibration calculates the intrinsic and extrinsic parameters,
    as well as the mean reprojection error.

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    @classmethod
    def create_from_plate(cls, calibration_plate: CalibrationPlate) -> CameraCalibration:
        """
        Creates an instance of class CameraCalibration.

        For a camera calibration a calibration plate is needed.

        :param calibration_plate: A calibration plate.

        :return: A new instance of CameraCalibration.

        .. versionadded:: ids_peak_icv 1.1
        """
        return cls(_calibration_plate=calibration_plate)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create a CameraCalibration, please refer to the classmethods.

        .. versionadded:: ids_peak_icv 1.1
        """
        try:
            self._calibration_plate = kwargs["_calibration_plate"]
        except KeyError:
            raise NotPossibleException(
                "Cannot initialize {} with __init__. Please use a classmethod.".format(self.__class__.__name__))

    def process(self, images: ImageArray) -> CalibrationResult:
        """
        Applies the camera calibration and calculates the intrinsic and extrinsic
        camera parameters based on several views of a calibration pattern.
        Furthermore, it computes the mean reprojection error.

        .. note:: This operation disregards any specified image regions. It processes the entire image.

        :param images: A list of images containing a calibration plate in different poses.

        :raises MismatchException:              If no images are provided, or if the sizes of the images are different.
        :raises NotSupportedException:          If the pattern of the calibration plate is not supported or
                                                the image has an unsupported format.
        :raises TargetNotFoundException:        If the marker points were not found on the given image.

        .. versionadded:: ids_peak_icv 1.1
        """
        if not isinstance(images, np.ndarray):
            raise NotSupportedException(
                "Parameter images has to be a numpy array of ids_peak_icv or ids_peak_ipl images.")

        _images = []
        for image in images:
            _images.append(_check_and_get_icv_image(image))

        image_handles = create_array(ctypes.c_void_p, len(_images))
        transform(_images, image_handles, lambda image: image._handle)

        result_handle = peak_icv_calibration_result_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Result_Create,
                                     ctypes.pointer(result_handle))
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Calibration_Process, self._calibration_plate._handle,
                                     image_handles,
                                     ctypes.c_size_t(len(image_handles)), ctypes.pointer(result_handle))

        return CalibrationResult(_handle=result_handle)
