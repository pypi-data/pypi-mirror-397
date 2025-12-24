# @package WorkspaceCalibration

from __future__ import annotations
import ctypes
from typing import Union, Any

from ids_peak_icv import lib_loader
from ids_peak_icv.exceptions import NotPossibleException, NotSupportedException
from ids_peak_icv.calibration.calibration_parameters import CalibrationParameters
from ids_peak_icv.calibration.intrinsic_parameters import IntrinsicParameters
from ids_peak_icv.calibration.calibration_result import CalibrationResult
from ids_peak_icv.calibration.calibration_plate import CalibrationPlate
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image, _check_and_get_icv_image
from ids_peak_ipl import ids_peak_ipl


class WorkspaceCalibration:
    """
    Class for calibrating a workspace.

    The WorkspaceCalibration calculates the extrinsic parameters based on a single image.

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    @classmethod
    def create_from_intrinsics_and_plate(cls, intrinsic_parameters: IntrinsicParameters,
                                         calibration_plate: CalibrationPlate) -> WorkspaceCalibration:
        """
        Creates an instance of class WorkspaceCalibration.

        In order to perform a workspace calibration, intrinsic parameters and a calibration plate must be provided.

        :param intrinsic_parameters: Can be obtained using e.g. CameraCalibration.process() or
                                     CalibrationParameters.create_from_file().
        :param calibration_plate:    A calibration plate.

        .. versionadded:: ids_peak_icv 1.1
        """

        return cls(_intrinsic_parameters=intrinsic_parameters, _calibration_plate=calibration_plate)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create a WorkspaceCalibration, please refer to the classmethods.

        .. versionadded:: ids_peak_icv 1.1
        """
        try:
            self._intrinsic_parameters = kwargs["_intrinsic_parameters"]
            self._calibration_plate = kwargs["_calibration_plate"]
        except KeyError:
            raise NotPossibleException(
                "Cannot initialize {} with __init__. Please use a classmethod.".format(self.__class__.__name__))

    def process(self, image: Union[Image, ids_peak_ipl.Image]) -> CalibrationResult:
        """
        Applies the workspace calibration and calculates the extrinsic camera parameters based on a single view of a
        calibration pattern.
        Furthermore, it computes the mean reprojection error.

        .. note:: This operation disregards any specified image regions. It processes the entire image.

        :param image: An image containing a single calibration plate.

        :raises NotPossibleException:       If no image is provided.
        :raises NotSupportedException:      If the image format is not supported.
        :raises MismatchException:          If the sizes of the image is different to the one given
                                            in the intrinsic parameters.
        :raises TargetNotFoundException:    If the images does not contain any calibration plate.

        .. versionadded:: ids_peak_icv 1.1
        """
        if not isinstance(image, (Image, ids_peak_ipl.Image)):
            raise NotSupportedException(
                "The given parameter type is not supported, only Images are supported.")

        _image = _check_and_get_icv_image(image)

        calibration_result = CalibrationResult._create_empty()

        execute_and_map_return_codes(lib_loader.dll().peak_icv_WorkspaceCalibration_Process,
                                     self._calibration_plate._handle,
                                     self._intrinsic_parameters._parameters,
                                     ctypes.sizeof(self._intrinsic_parameters._parameters),
                                     _image._handle, ctypes.pointer(calibration_result._handle))

        return calibration_result
