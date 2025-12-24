from __future__ import annotations

import ctypes
from enum import IntEnum
from typing import Union, TypeAlias, Callable, Iterable, Any, cast, Type, TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from ids_peak_ipl import ids_peak_ipl

from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_point_cloud_handle, peak_icv_point_xyz, peak_icv_point_xyzi
from ids_peak_icv.backend.utils import execute_and_map_return_codes, create_array
from ids_peak_icv.exceptions import NotPossibleException, NotSupportedException, MismatchException
from ids_peak_icv.datatypes.geometry.point_xyz import PointXYZ
from ids_peak_icv.datatypes.geometry.point_xyzi import PointXYZI
from ids_peak_icv.datatypes.image import Image, _check_and_get_icv_image
from ids_peak_icv.datatypes.xyz_image import XYZImage

if TYPE_CHECKING:
    from ids_peak_icv.datatypes.undistorted_image import UndistortedImage
    from ids_peak_icv.calibration.extrinsic_parameters import ExtrinsicParameters

# Note: We loose type info here, as it is stored as a pointer to a python object
XYZArray: TypeAlias = npt.NDArray[np.object_]
XYZIArray: TypeAlias = npt.NDArray[np.object_]


class PointCloudPointType(IntEnum):
    """
    Enumeration representing different types of point cloud points.

    Attributes:
        XYZ: Represents a point with X, Y and Z coordinates.
        XYZ_I8: Represents a point with X, Y, Z coordinates and 8-bit intensity.
        XYZ_I10: Represents a point with X, Y, Z coordinates and 10-bit intensity.
        XYZ_I12: Represents a point with X, Y, Z coordinates and 12-bit intensity.

    .. ingroup:: ids_peak_icv_python_types
    .. versionadded:: ids_peak_icv 1.1
    """
    XYZ = 0
    XYZ_I8 = 1
    XYZ_I10 = 2
    XYZ_I12 = 3


class PointCloud:
    """
    A point cloud is a set of data points defined in a three-dimensional (3D) coordinate system.

    Each point is represented by its X, Y, and Z coordinates,
    specifying its exact position in 3D space. Optionally it can contain intensity metadata.
    Point clouds are often generated from depth maps,
    such as those obtained from a time-of-flight camera.
    They serve as a detailed digital representation of the shape and size of physical objects,
    enabling precise measurements and analysis.

    .. ingroup:: ids_peak_icv_python_types
    .. versionadded:: ids_peak_icv 1.1
    """

    @classmethod
    def create_from_xyz_image(cls, xyz_image: XYZImage,
                              intensity_image: Union[Image, ids_peak_ipl.Image, None] = None) -> PointCloud:
        """
        Creates a point cloud from a xyz image and optional metadata.

        .. note:: The region of the metadata image is disregarded.

        :param xyz_image: XYZ image providing the spatial information.
        :param intensity_image: Image that holds the meta information (e.g. an intensity image).
        :return: Created point cloud instance

        :raises MismatchException: If the xyz_image and the intensity image don't have the same size.

        .. versionadded:: ids_peak_icv 1.1
        """
        return cls(_xyz_image=xyz_image, _intensity_image=intensity_image)

    @classmethod
    def create_from_undistorted_depth_map(cls, undistorted_depth_map: UndistortedImage,
                                          intensity_image: Union[
                                              Image, ids_peak_ipl.Image, None] = None) -> PointCloud:
        """
        Creates a point cloud from an undistorted depth map and optional metadata.

        .. note:: The region of the metadata image is disregarded.

        :param undistorted_depth_map: Undistorted image providing the radial depth information.
        :param intensity_image: Image that holds the meta information (e.g. an intensity image).
        :return: Created point cloud instance

        :raises MismatchException: If the undistorted_depth_map and the intensity image don't have the same size.

        .. versionadded:: ids_peak_icv 1.1
        """
        return cls(_xyz_image=XYZImage.create_from_undistorted_image(undistorted_depth_map),
                   _intensity_image=intensity_image)

    @classmethod
    def create_from_points(cls, points: Union[XYZArray, XYZIArray],
                           point_type: PointCloudPointType) -> PointCloud:
        """
        Creates a point cloud from points.

        :param points: An array of PointXYZ or PointXYZI.
        :param point_type: The type of point.

        :return: Created point cloud instance

        :raises MismatchException: If Parameter points is not a numpy array of PointXYZ or PointXYZI objects
                                   matching the point_type.

        .. versionadded:: ids_peak_icv 1.1
        """
        handle = peak_icv_point_cloud_handle()

        c_point_type: Type[peak_icv_point_xyz] | Type[peak_icv_point_xyzi]
        if point_type == PointCloudPointType.XYZ:
            c_point_type = peak_icv_point_xyz
        elif (point_type == PointCloudPointType.XYZ_I8 or
              point_type == PointCloudPointType.XYZ_I10 or
              point_type == PointCloudPointType.XYZ_I12):
            c_point_type = peak_icv_point_xyzi
        else:
            raise NotSupportedException("The given point type {} is not supported".format(point_type.name))

        size = len(points)
        c_points = create_array(c_point_type, size)

        for i, p in enumerate(points):
            if isinstance(p, PointXYZI) and isinstance(points,
                                                       np.ndarray) and point_type != PointCloudPointType.XYZ:
                c_points[i] = peak_icv_point_xyzi(p.x, p.y, p.z, p.intensity)
            elif isinstance(p, PointXYZ) and isinstance(points,
                                                        np.ndarray) and point_type == PointCloudPointType.XYZ:
                c_points[i] = peak_icv_point_xyz(p.x, p.y, p.z)
            else:
                raise MismatchException(
                    "Parameter points has to be a numpy array of PointXYZ or PointXYZI objects and "
                    "the point_type has to match it.")

        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_CreateFromPoints,
                                     ctypes.pointer(handle), c_points, ctypes.c_size_t(size),
                                     ctypes.c_int(point_type))

        return cls(_handle=handle, _point_type=point_type)

    @classmethod
    def create_from_file(cls, file_path: str,
                         point_type: PointCloudPointType = PointCloudPointType.XYZ) -> PointCloud:
        """
        Loads a point cloud from a file.

        The chosen file type is determined by the given extension.

        The following file formats are supported:
        - [PLY]

        :param file_path: The file is loaded from the file path, which should encompass both the directory path and the
                          filename.
        :param point_type: Defines whether the point cloud is loaded with or without meta information and how the meta
                           information is interpreted.

        :return: The point cloud, which was loaded from the file.

        :raises IOException: If the specified file path is invalid, you lack the necessary permissions, or the file
        already exists.

        .. versionadded:: ids_peak_icv 1.1
        """
        handle = peak_icv_point_cloud_handle()

        c_file_path = file_path.encode('utf-8')
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_CreateFromFile,
                                     ctypes.pointer(handle),
                                     ctypes.c_int(point_type),
                                     ctypes.c_char_p(c_file_path),
                                     ctypes.c_size_t(len(c_file_path)))

        return PointCloud(_handle=handle, _point_type=point_type)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create a point cloud, please refer to the class methods.

        .. versionadded:: ids_peak_icv 1.1
        """

        self._handle = None
        self._sorted_points_cache: np.ndarray | None = None
        self._points: np.ndarray | None = None
        self._point_type = None

        if "_handle" in kwargs:
            self._point_type = kwargs["_point_type"]
            self._handle = kwargs["_handle"]
            return
        elif "_xyz_image" not in kwargs:
            raise NotPossibleException(
                "Cannot initialize {} with __init__. Please use a classmethod.".format(self.__class__.__name__))

        xyz_image = _check_and_get_icv_image(kwargs["_xyz_image"])
        if "_intensity_image" in kwargs:
            meta_data = _check_and_get_icv_image(kwargs["_intensity_image"])
        else:
            meta_data = None

        xyz_image_handle = xyz_image._handle

        self._handle = peak_icv_point_cloud_handle()

        try:
            if meta_data is None:
                execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_CreateFromXYZImage,
                                             ctypes.pointer(self._handle), xyz_image_handle)
            else:
                image_handle = meta_data._handle
                execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_CreateFromXYZImageAndIntensityImage,
                                             ctypes.pointer(self._handle), xyz_image_handle, image_handle)
        except Exception as e:
            # Cause the __del__ method is called if a handle is already created, we have to set the handle back to None
            # and reraise the exception.
            self._handle = None
            raise e

        self._init_point_type()

    def transform(self, matrix: npt.NDArray) -> PointCloud:
        """
        Applies a transformation of a point cloud based on the given matrix.

        :param matrix: The transformation matrix
        :return: A new transformed point cloud.

        :raises NotPossibleException:  If the dtype of numpy array isn't type float32 or the matrix size isn't 4x4.

        .. versionadded:: ids_peak_icv 1.1
        """
        if matrix.dtype != np.float32:
            raise NotPossibleException(
                "Matrix has wrong numpy array type. dtype has to be float32.")

        if matrix.shape != (4, 4):
            raise NotPossibleException(
                f"Matrix has wrong shape {matrix.shape}. Shape has to be (4,4).")

        handle = peak_icv_point_cloud_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_Create,
                                     ctypes.pointer(handle))
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_Transform,
                                     self._handle, matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                                     ctypes.pointer(handle))

        return PointCloud(_handle=handle, _point_type=self._point_type)

    def transform_to_workspace(self, extrinsic_parameters: ExtrinsicParameters) -> PointCloud:
        """
        Transforms a point cloud to the workspace coordinate system using the extrinsic parameters.

        The point cloud is transformed from the camera coordinate system to the workspace coordinate system
        using the inverse of the extrinsic parameters.

        :param extrinsic_parameters: Extrinsic parameters of the workspace calibration.
        :return: A new transformed point cloud.

        .. versionadded:: ids_peak_icv 1.1
        """

        handle = peak_icv_point_cloud_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_Create,
                                     ctypes.pointer(handle))
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_TransformToWorkspace,
                                     self._handle, extrinsic_parameters._parameters,
                                     ctypes.sizeof(extrinsic_parameters._parameters),
                                     ctypes.pointer(handle))

        return PointCloud(_handle=handle, _point_type=self._point_type)

    @property
    def points(self) -> Union[XYZArray, XYZIArray]:
        """
        Get the points of the point cloud.

        :return: List of Point objects representing the point clouds points.

        .. versionadded:: ids_peak_icv 1.1
        """
        if self._points is not None:
            return cast(Union[XYZArray, XYZIArray], self._points)

        if self._point_type == PointCloudPointType.XYZ:
            self._init_points(peak_icv_point_xyz, PointXYZ,
                              lambda c_points: (PointXYZ(p.x, p.y, p.z) for p in c_points))
        elif (self._point_type == PointCloudPointType.XYZ_I8 or
              self._point_type == PointCloudPointType.XYZ_I10 or
              self._point_type == PointCloudPointType.XYZ_I12):
            self._init_points(peak_icv_point_xyzi, PointXYZI,
                              lambda c_points: (PointXYZI(p.x, p.y, p.z, p.i) for p in c_points))
        else:
            raise NotSupportedException("The given point type is invalid")

        return cast(Union[XYZArray, XYZIArray], self._points)

    def __eq__(self, other: object) -> bool:
        """
        Check if two point clouds are equal.

        :param other: Another point cloud object

        :return: True if point clouds are equal, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """
        if isinstance(other, PointCloud):
            if self._handle == other._handle:
                return True

            if self._sorted_points_cache is None:
                self._sorted_points_cache = np.sort(self.points, axis=None)

            if other._sorted_points_cache is None:
                other._sorted_points_cache = np.sort(other.points, axis=None)

            return np.array_equal(self._sorted_points_cache, other._sorted_points_cache)

        if isinstance(other, list) or isinstance(other, tuple):
            if len(self.points) != len(other):
                return False

            if self._sorted_points_cache is None:
                self._sorted_points_cache = np.sort(self.points, axis=None)

            other_points = [PointXYZ(p[0], p[1], p[2]) for p in other]
            sorted_other_points = sorted(other_points)

            for i in range(len(self._sorted_points_cache)):
                if self._sorted_points_cache[i] != sorted_other_points[i]:
                    return False
            return True

        return False

    def __ne__(self, other: object) -> bool:
        """
        Check if two point clouds are not equal.

        :param other: Another point cloud object

        :return: True if point clouds are not equal, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """
        return not self.__eq__(other)

    def __del__(self) -> None:
        if self._handle is not None:
            lib_loader.dll().peak_icv_PointCloud_Destroy(self._handle)

    def __repr__(self) -> str:
        """
        Get a string representation of the Point Cloud represented by points.

        :return: String representation of the Point Cloud

        .. versionadded:: ids_peak_icv 1.1
        """
        return f"({', '.join(map(str, self.points))})"

    def save(self, file_path: str) -> None:
        """
        Saves point cloud to file.

        The chosen file type is determined by the given extension.

        The following file formats are supported:
        - [PLY](only binary)

        If no file extension is provided, .ply is automatically added.

        :param file_path: The file is saved to the file_path, which should encompass both the directory path and the
                          filename.

        :raises IOException: The specified file path is invalid or lacks write permissions.

        .. versionadded:: ids_peak_icv 1.1
        """
        c_file_path = file_path.encode('utf-8')
        lib_loader.dll().peak_icv_PointCloud_SaveToFile(self._handle,
                                                          ctypes.c_char_p(c_file_path),
                                                          ctypes.c_size_t(len(c_file_path)))

    def _init_points(self, c_type: Type[ctypes.Structure], python_type: Type,
                     func: Callable[[ctypes.Array], Iterable[Any]]) -> None:

        c_num_points = ctypes.c_size_t()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_GetPoints_GetCount,
                                     self._handle, ctypes.pointer(c_num_points))

        if c_num_points.value == 0:
            self._points = np.ndarray(0)
            return

        c_size_in_bytes_points = ctypes.c_size_t()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_GetPoints_GetSizeInBytes,
                                     self._handle, ctypes.pointer(c_size_in_bytes_points))

        c_points = create_array(c_type, c_num_points.value)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_GetPoints,
                                     self._handle, c_points, c_size_in_bytes_points)
        iterable = func(c_points)
        # workaround to fill the array on python3.7 with numpy
        self._points = np.empty(len(c_points), dtype=python_type)

        for i, it in enumerate(iterable):
            self._points[i] = it

    def _init_point_type(self) -> None:
        point_type = ctypes.c_int()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_PointCloud_GetType, self._handle,
                                     ctypes.pointer(point_type))
        self._point_type = PointCloudPointType(point_type.value)
