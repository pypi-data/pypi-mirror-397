from __future__ import annotations
import ctypes
from enum import Enum
from typing import Union, Any

from ids_peak_common.datatypes.metadata import Metadata
from ids_peak_icv import lib_loader
from ids_peak_icv.calibration.intrinsic_parameters import IntrinsicParameters
from ids_peak_icv.backend.datatypes import peak_icv_intrinsic_parameters, peak_icv_undistortion_handle
from ids_peak_icv.backend.utils import (execute_and_map_return_codes, metadata_to_capture_information,
                                          check_init_for_classes_with_classmethods_only)
from ids_peak_icv.datatypes.image import Image, _check_and_get_icv_image
from ids_peak_icv.datatypes.undistorted_image import UndistortedImage
from ids_peak_common.datatypes.geometry.size import Size
from ids_peak_ipl import ids_peak_ipl


class Interpolation(Enum):
    """
    Enumeration of interpolation methods used in image transformations.

    These methods determine how pixel values are calculated
    when performing geometric transformations on images,
    such as undistortion and scaling.

    .. versionadded:: ids_peak_icv 1.1
    .. ingroup:: ids_peak_icv_python_transformations
    """

    BILINEAR = 0
    """
    Calculates the output pixel value
    as a weighted average of the four closest input pixels.
    Suitable for smoother results.
    """

    NEAREST_NEIGHBOR = 1
    """
    Uses the nearest input pixel value directly.
    Faster but may introduce aliasing or blocky artifacts.
    """


class Undistortion:
    """
    Represents an undistortion transformation for images.

    Provides geometric correction
    to remove lens distortion using intrinsic calibration parameters.
    The parameters can be obtained using `CameraCalibration.process()`.

    This class also supports undistorting images with binning factors
    that differ from those used during calibration,
    as long as the image metadata includes valid binning information.
    The binning factor of the image to be undistorted
    must be greater than or equal
    to that of the calibration images.

    .. note::
       If the metadata of the images to be undistorted
       differs from the metadata used during calibration (e.g. due to different binning),
       internal parameters may need to be reinitialized.
       In such cases, the first call to `process()` may take longer.
       To avoid this,
       call `set_capture_information()` beforehand
       with matching metadata.

    ### Limitations
    - In-place undistortion is not supported.
    - Maximum supported image size is 32767 × 32767 pixels.

    .. versionadded:: ids_peak_icv 1.1
    .. ingroup:: ids_peak_icv_python_transformations
    """

    _intrinsic_parameters: IntrinsicParameters

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create an Image, please refer to the classmethods ``create_from_intrinsics`` and
        ``create_from_intrinsics_and_metadata``.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._handle = check_init_for_classes_with_classmethods_only(self.__class__.__name__,
                                                                     peak_icv_undistortion_handle,
                                                                     *args, **kwargs)

        if len(kwargs):
            self._handle = kwargs["_handle"]
            self._new_intrinsic_parameters = kwargs["_new_intrinsic_parameters"]

    @classmethod
    def create_from_intrinsics(cls, intrinsic_parameters: IntrinsicParameters) -> Undistortion:
        """

        :param intrinsic_parameters: Intrinsic parameters derived from a camera calibration.
        :return:

        .. versionadded:: ids_peak_icv 1.1
        """
        cls._intrinsic_parameters = intrinsic_parameters
        cls._new_intrinsic_parameters = peak_icv_intrinsic_parameters()
        cls._handle = peak_icv_undistortion_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Transform_Undistortion_Create,
                                     ctypes.pointer(cls._handle),
                                     cls._intrinsic_parameters._parameters,
                                     ctypes.sizeof(cls._intrinsic_parameters._parameters),
                                     ctypes.pointer(cls._new_intrinsic_parameters))

        return cls(_handle=cls._handle, _new_intrinsic_parameters=cls._new_intrinsic_parameters)

    @classmethod
    def create_from_intrinsics_and_metadata(cls, intrinsic_parameters: IntrinsicParameters,
                                            metadata: Metadata) -> Undistortion:
        """

        :param intrinsic_parameters: Intrinsic parameters derived from a camera calibration.
        :param metadata: Metadata of an image which contains information about the image capture settings.
        :return:
        .. versionadded:: ids_peak_icv 1.1
        """
        cls._intrinsic_parameters = intrinsic_parameters
        cls._new_intrinsic_parameters = peak_icv_intrinsic_parameters()
        cls._handle = peak_icv_undistortion_handle()
        c_capture_information = metadata_to_capture_information(metadata)
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Transform_Undistortion_Create_With_Image_CaptureInformation,
            ctypes.pointer(cls._handle),
            cls._intrinsic_parameters._parameters,
            ctypes.sizeof(cls._intrinsic_parameters._parameters),
            c_capture_information, ctypes.sizeof(c_capture_information),
            ctypes.pointer(cls._new_intrinsic_parameters))

        return cls(_handle=cls._handle, _new_intrinsic_parameters=cls._new_intrinsic_parameters)

    def __del__(self) -> None:
        """
        Destroys the undistortion object and releases any associated resources.

        .. versionadded:: ids_peak_icv 1.1
        """
        if hasattr(self, '_handle'):
            lib_loader.dll().peak_icv_Image_Destroy(self._handle)

    def process(self, image: Union[Image, ids_peak_ipl.Image]) -> UndistortedImage:
        """
        Applies undistortion to the specified image.

        This function undistorts the image
        and returns an `UndistortedImage` that includes updated intrinsic parameters.

        The returned image has the same size and pixel format as the input image.

        .. note::
            If the input image specifies a region, that region is also undistorted.
            When no region is specified (i.e., the full image is used), the output will also
            represent the full image.

        :param image:
            The image to be undistorted.

        @supportedPixelformats{Undistortion}

        :return:
            An undistorted image with updated intrinsic parameters.

        :raises NotPossibleException:
            The image binning factor is too small
            for the undistortion configuration.
        :raises MismatchException:
            The image size or capture information
            does not match the undistortion configuration.

        .. versionadded:: ids_peak_icv 1.1
        """
        _image = _check_and_get_icv_image(image)

        output_image = Image.create_from_pixel_format_and_size(_image._pixel_format,
                                                               Size(_image.width, _image.height))

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Transform_Undistortion_Process,
                                     self._handle,
                                     _image._handle,
                                     output_image._handle)

        return UndistortedImage(output_image,
                                IntrinsicParameters(_parameters=self._new_intrinsic_parameters))

    @property
    def interpolation(self) -> Interpolation:
        """
        :return:
            The current @ref Interpolation "interpolation method" used by the undistortion.

        .. versionadded:: ids_peak_icv 1.1
        """
        interpolation = ctypes.c_size_t()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Transform_Undistortion_GetInterpolation,
                                     self._handle,
                                     ctypes.pointer(interpolation))

        return Interpolation(interpolation.value)

    @interpolation.setter
    def interpolation(self, interpolation: Interpolation) -> None:
        """
        Sets the @ref Interpolation "interpolation method" used for undistortion.

        :param interpolation:
            @ref Interpolation "Interpolation method" to use.

        .. versionadded:: ids_peak_icv 1.1
        """
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Transform_Undistortion_SetInterpolation,
                                     self._handle,
                                     ctypes.c_size_t(interpolation.value))
