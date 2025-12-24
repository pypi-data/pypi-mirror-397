from __future__ import annotations

import ctypes
from typing import Union, TypeAlias, Any, cast, TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from ids_peak_common.datatypes.geometry.point import Point
from ids_peak_common.datatypes.geometry.rectangle import Rectangle

from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import (peak_icv_region_handle, peak_icv_point, peak_icv_point_f,
                                              peak_icv_drawing_options, peak_common_rectangle)
from ids_peak_icv.backend.utils import create_array, execute_and_map_return_codes
from ids_peak_icv.exceptions import (NotSupportedException, OutOfRangeException, NotPossibleException,
                                       ICVException)
from ids_peak_icv.painting.drawable import IDrawable
from ids_peak_icv.painting.drawing_options import DrawingOptions

if TYPE_CHECKING:
    from ids_peak_icv.datatypes.image import Image

# Note: We loose type info here, as it is stored as a pointer to a python object
PointArray: TypeAlias = npt.NDArray[np.object_]
RegionArray: TypeAlias = npt.NDArray[np.object_]


class Region(IDrawable):
    """
    Represents a region consisting of a set of points in the image plane.

    @see @ref concept_type_region

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_types
    """

    @classmethod
    def create_from_points(cls, points: Union[PointArray, npt.NDArray[np.int_]]) -> Region:
        """
        Creates a region from points.

        :param points: NumPy Array of Point objects representing the region's points OR NumPy Array of Points [x,y]
        :return: A region instance.

        :raises OutOfRangeException: If a point at a given index has an invalid length.
        :raises NotSupportedException: If the parameter `points` is not a NumPy array of Point objects or
                                       a two-dimensional NumPy array.

        .. versionadded:: ids_peak_icv 1.0
        """
        size = len(points)
        c_points = create_array(peak_icv_point, size)

        for i, p in enumerate(points):
            if isinstance(p, Point) and isinstance(points, np.ndarray):
                c_points[i] = peak_icv_point(p.x, p.y)
            elif isinstance(p, np.ndarray):
                if len(p) == 2:
                    c_points[i] = peak_icv_point(p[0], p[1])
                else:
                    raise OutOfRangeException(
                        "Point {index} has invalid length {length}".format(index=i, length=len(p)))
            else:
                raise NotSupportedException(
                    "Parameter points has to be a numpy array of Point objects or a two-dimensional numpy array.")

        handle = peak_icv_region_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_CreateFromPoints,
                                     ctypes.pointer(handle), c_points, size)

        return Region(_handle=handle)

    @classmethod
    def create_from_rectangle(cls, rect: Rectangle) -> Region:
        """
        Creates a Region from a Rectangle.
        :param rect: Rectangle to create the region from

        :return: A region instance.

        :raises NotSupportedException: If the contents of rectangle are not integers.

        .. versionadded:: ids_peak_icv 1.0
        """

        c_rect = None
        try:
            c_rect = peak_common_rectangle(rect.x, rect.y, rect.width, rect.height)
        except TypeError:
            raise NotSupportedException("The contents of rectangle must be integer.")

        handle = peak_icv_region_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_CreateFromRectangle,
                                     ctypes.pointer(handle), c_rect)

        return Region(_handle=handle)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create an _empty Region_ create it with no arguments, in all other cases please refer to the
        classmethods.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        self._handle = peak_icv_region_handle(None)

        if len(args) or len(kwargs):
            def _check_init_for_classes_with_classmethods_only(**kwargs: Any) -> peak_icv_region_handle:
                try:
                    return cast(peak_icv_region_handle, kwargs["_handle"])
                except KeyError:
                    raise NotPossibleException(
                        "Cannot initialize Region with arguments. Please use a classmethod or create an empty Region "
                        "using Region().")

            self._handle = _check_init_for_classes_with_classmethods_only(**kwargs)
        else:
            handle = peak_icv_region_handle()
            execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Create,
                                         ctypes.pointer(handle))
            self._handle = handle

        self._points: np.ndarray | None = None
        self._connected_components: np.ndarray | None = None

    def __eq__(self, other: object) -> bool:
        """
        Check if two regions are equal.

        :param other: Another Region object

        :return: True if regions are equal, False otherwise

        .. versionadded:: ids_peak_icv 1.0
        """
        if not isinstance(other, Region):
            return False

        if self._handle == other._handle:
            return True

        is_equal = ctypes.c_bool()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Compare, self._handle, other._handle,
                                     ctypes.pointer(is_equal))

        return is_equal.value

    def __ne__(self, other: object) -> bool:
        """
        Check if two regions are not equal.

         :param other: Another Region object

        :return: True if regions are not equal, False otherwise

        .. versionadded:: ids_peak_icv 1.0
        """
        return not self.__eq__(other)

    @property
    def points(self) -> PointArray:
        """
        Get the points of the region.

        :return: List of Point objects representing the region's points.

        .. versionadded:: ids_peak_icv 1.0
        """
        if self._points is not None:
            return self._points

        c_num_points = ctypes.c_size_t()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_GetPoints_GetCount,
                                     self._handle, ctypes.pointer(c_num_points))

        if c_num_points.value == 0:
            self._points = np.ndarray(0)
            return cast(PointArray, self._points)

        c_points = create_array(peak_icv_point, c_num_points.value)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_GetPoints,
                                     self._handle, c_points, c_num_points)

        iterable = (Point(p.x, p.y) for p in c_points)

        # workaround to fill the array on python3.7 with numpy
        self._points = np.empty(len(c_points), dtype=Point)
        for i, it in enumerate(iterable):
            self._points[i] = it

        return cast(PointArray, self._points)

    @property
    def connected_components(self) -> RegionArray:
        """
        Calculate the connected components of the region.

        The 8-neighborhood is used to determine the components.

        @see @ref concept_region_connected-components

        :return: List of connected components as Region objects.

        .. versionadded:: ids_peak_icv 1.0
        """
        if self._connected_components is not None:
            return self._connected_components

        c_num_regions = ctypes.c_size_t()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Region_GetConnectedComponents_GetCount,
            self._handle, ctypes.pointer(c_num_regions))

        if c_num_regions.value == 0:
            self._connected_components = np.ndarray(0)
            return cast(RegionArray, self._connected_components)

        c_regions = create_array(peak_icv_region_handle, c_num_regions.value)

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Array_Create, c_regions,
                                     c_num_regions)
        try:
            execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_GetConnectedComponents,
                                         self._handle, c_regions, c_num_regions)
            iterable = (Region(_handle=h) for h in c_regions)
        except ICVException as e:
            lib_loader.dll().peak_icv_Region_Array_Destroy(c_regions, c_num_regions)
            raise e

        # workaround to fill the array on python3.7 with numpy
        self._connected_components = np.empty(len(c_regions), dtype=Region)
        for i, it in enumerate(iterable):
            self._connected_components[i] = it

        return cast(RegionArray, self._connected_components)

    @property
    def area(self) -> int:
        """
        Calculate the area of the region. The area is the number of pixels in the region.

        :return: Area of the region.

        .. versionadded:: ids_peak_icv 1.0
        """
        c_area = ctypes.c_size_t()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_GetArea,
                                     self._handle, ctypes.pointer(c_area))

        return c_area.value

    @property
    def center_of_gravity(self) -> Point:
        """
        Calculate the center of gravity of the region.

        :return: Center of gravity as a PointF object.

        :raises MathErrorException: If the center of gravity could not be computed.

        .. versionadded:: ids_peak_icv 1.0
        """
        c_center_of_gravity = peak_icv_point_f()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_GetCenterOfGravity,
                                     self._handle, ctypes.pointer(c_center_of_gravity))

        return Point(c_center_of_gravity.x, c_center_of_gravity.y)

    def intersection(self, other_region: Region) -> Region:
        """
        Computes the intersection of two regions.

        :return: The intersection of two regions.

        .. versionadded:: ids_peak_icv 1.0
        """
        output_region = Region()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Intersection,
                                     self._handle, other_region._handle, ctypes.pointer(output_region._handle))

        return output_region

    def difference(self, other_region: Region) -> Region:
        """
        Computes the difference of two regions.

        :return: The difference of two regions.

        .. versionadded:: ids_peak_icv 1.0
        """
        output_region = Region()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Difference,
                                     self._handle, other_region._handle, ctypes.pointer(output_region._handle))

        return output_region

    def union(self, other_region: Region) -> Region:
        """
        Computes the union of two regions.

        :return: The united region.

        .. versionadded:: ids_peak_icv 1.0
        """
        output_region = Region()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Union,
                                     self._handle, other_region._handle, ctypes.pointer(output_region._handle))

        return output_region

    def dilation(self, structuring_element: Region) -> Region:
        """
        Computes the dilation of the input region with the given structuring element.

        The reference point of the structuring element is at (0, 0).

        :param structuring_element:

        :return: The dilated region.

        .. versionadded:: ids_peak_icv 1.0
        """
        output_region = Region()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Dilation, self._handle,
                                     structuring_element._handle, ctypes.pointer(output_region._handle))
        return output_region

    def erosion(self, structuring_element: Region) -> Region:
        """
        Computes the erosion of the input region with the given structuring element.

        The reference point of the structuring element is at (0, 0).

        :param structuring_element:

        :return: The eroded region.

        .. versionadded:: ids_peak_icv 1.0
        """
        output_region = Region()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Erosion, self._handle,
                                     structuring_element._handle, ctypes.pointer(output_region._handle))
        return output_region

    def __del__(self) -> None:
        """
        Destructor for Region class.
        """
        if self._handle is not None:
            lib_loader.dll().peak_icv_Region_Destroy(self._handle)

    def _draw(self, image: Image, drawing_options: DrawingOptions) -> None:
        """
        Only region points inside the image are painted.
        Region points outside the image are ignored. In case of an empty region, the image is not modified.

        .. versionadded:: ids_peak_icv 1.0
        """
        from ids_peak_icv.datatypes.image import _check_and_get_icv_image

        drawing_options_c = peak_icv_drawing_options(drawing_options.color.color_code,
                                                       drawing_options.opacity.value)

        _image = _check_and_get_icv_image(image)

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Draw, _image._handle,
                                     self._handle, drawing_options_c)
