from __future__ import annotations

from typing import Any

import numpy as np

from ids_peak_icv.datatypes.binning_factor import BinningFactor
from ids_peak_common.datatypes.geometry.point import Point
from ids_peak_common.datatypes.geometry.size import Size
from ids_peak_icv.backend.datatypes import peak_icv_intrinsic_parameters, ctypes_objects_equal
from ids_peak_icv.exceptions import NotPossibleException


class IntrinsicParameters:
    """
    Class for intrinsic parameters.

    The intrinsic parameters contain the necessary information to use the camera calibration.

    This class contains only the intrinsic parameters. These parameters are essential for image
    operations like point cloud generation, image undistortion, and other calibration-dependent operations.

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create IntrinsicParameters, please refer to the classmethods.

        .. versionadded:: ids_peak_icv 1.1
        """
        try:
            self._parameters: peak_icv_intrinsic_parameters = kwargs["_parameters"]
        except KeyError:
            raise NotPossibleException("{} shall not be initialized".format(self.__class__.__name__))

    @property
    def principle_point(self) -> Point:
        """
        Returns the principle point.

        :return: Point representing the principle point.

        .. versionadded:: ids_peak_icv 1.1
        """
        return Point(
            self._parameters.principle_point.x, self._parameters.principle_point.y)

    @property
    def distortion_coefficients(self) -> np.ndarray:
        """
        Returns the distortion coefficients.

        :return: A numpy array of size 14 containing the distortion coefficients.

        .. versionadded:: ids_peak_icv 1.1
        """

        coefficients = (list(self._parameters.distortion_coefficients.radial_distortion.coefficients)
                        + list(self._parameters.distortion_coefficients.tangential_distortion.coefficients)
                        + list(self._parameters.distortion_coefficients.prism_distortion.coefficients)
                        + list(self._parameters.distortion_coefficients.tilt_distortion.coefficients))

        return np.array(coefficients, dtype=np.float32)

    @property
    def focal_length_pixel_size_ratio(self) -> Point:
        """
        Returns the focal length pixel size ratio.

        :return: Point representing the focal length pixel size ratio.

        .. versionadded:: ids_peak_icv 1.1
        """
        return Point(
            self._parameters.focal_length_pixel_size_ratio.x, self._parameters.focal_length_pixel_size_ratio.y)

    @property
    def image_size(self) -> Size:
        """
        Returns image size

        :return: Size representing the image size.

        .. versionadded:: ids_peak_icv 1.1
        """
        return Size(
            self._parameters.image_size.width, self._parameters.image_size.height)

    @property
    def binning_factor(self) -> BinningFactor:
        """
        Returns binning factor

        :return: Binning factor of the image.

        .. versionadded:: ids_peak_icv 1.1
        """
        return BinningFactor(self._parameters.binning_factor.x, self._parameters.binning_factor.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IntrinsicParameters):
            return False
        return ctypes_objects_equal(self._parameters, other._parameters)
