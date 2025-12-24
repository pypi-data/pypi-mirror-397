from __future__ import annotations

import ctypes
from typing import Any, TYPE_CHECKING

from ids_peak_common.datatypes.geometry.size import Size
from ids_peak_common.datatypes.pixelformat import PixelFormat
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_image_handle, peak_common_size
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.exceptions import NotPossibleException

if TYPE_CHECKING:
    from ids_peak_icv.datatypes.undistorted_image import UndistortedImage
    from ids_peak_icv.calibration.extrinsic_parameters import ExtrinsicParameters


class XYZImage(Image):
    """
    Transforms a depth map with radial coordinates to a three-channel image with cartesian coordinates.

    This class converts an undistorted depth map with radial coordinates to a three-channel image with cartesian coordinates.
    Radial coordinates represent the distance directly from the optical center to the reflected object, resulting in
    values that appear more distant as you move outwards from the image center. In contrast, Cartesian coordinates
    interpret the optical center as a plane, resulting in straight lines from the camera to the reflected object. For
    example, if the camera is placed in front of a flat wall, only the Cartesian values will show a flat plane.

    .. ingroup:: ids_peak_icv_python_types
    .. versionadded:: ids_peak_icv 1.1
    """

    @classmethod
    def create_from_undistorted_image(cls, undistorted_depth_map: UndistortedImage) -> XYZImage:
        """
        Creates an instance of XYZImage using an undistorted depth map image and intrinsic parameters

        :param undistorted_depth_map: Undistorted depth map with radial coordinates.

        .. versionadded:: ids_peak_icv 1.1
        """
        return cls(_undistorted_depth_map=undistorted_depth_map)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create a point cloud, please refer to the class methods.

        .. versionadded:: ids_peak_icv 1.1
        """
        if "_undistorted_depth_map" in kwargs:
            image = Image.create_from_pixel_format_and_size(PixelFormat.COORD3D_ABC32F,
                                                            Size(kwargs["_undistorted_depth_map"].width,
                                                                 kwargs["_undistorted_depth_map"].height))
            super().__init__(_handle=image._handle)
            image._handle = peak_icv_image_handle(None)  # necessary to ensure only one handle delete call

            execute_and_map_return_codes(lib_loader.dll().peak_icv_Transform_DepthMap_To_XYZImage,
                                         self._handle,
                                         kwargs["_undistorted_depth_map"].intrinsic_parameters._parameters,
                                         ctypes.sizeof(
                                             kwargs["_undistorted_depth_map"].intrinsic_parameters._parameters),
                                         kwargs["_undistorted_depth_map"]._handle)
        elif "_handle" in kwargs:
            super().__init__(_handle=kwargs["_handle"])
        else:
            raise NotPossibleException(
                "Cannot initialize {} with __init__. Please use a classmethod.".format(self.__class__.__name__))

    def transform_to_workspace(self, extrinsic_parameters: ExtrinsicParameters) -> XYZImage:
        """
        Transforms the image to workspace coordinates using the specified extrinsic parameters.

        The transformation uses the inverse of the extrinsic matrix
        to convert from camera to workspace coordinate system.

        :param extrinsic_parameters: Extrinsic parameters from the workspace calibration.

        .. versionadded:: ids_peak_icv 1.1
        """
        output_handle = peak_icv_image_handle()
        image_size = peak_common_size(self._size.width, self._size.height)

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_Create,
                                     ctypes.pointer(output_handle),
                                     ctypes.c_int(PixelFormat.COORD3D_ABC32F.value),
                                     image_size)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_TransformToWorkspace,
                                     self._handle,
                                     extrinsic_parameters._parameters, ctypes.sizeof(extrinsic_parameters._parameters),
                                     output_handle)

        return XYZImage(_handle=output_handle)
