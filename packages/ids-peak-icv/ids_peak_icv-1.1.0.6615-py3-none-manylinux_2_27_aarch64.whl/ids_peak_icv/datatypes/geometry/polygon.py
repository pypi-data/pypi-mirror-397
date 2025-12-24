from __future__ import annotations

import ctypes
from typing import Union, TypeAlias, Any, cast

import numpy as np
import numpy.typing as npt

from ids_peak_icv import lib_loader
from ids_peak_icv.exceptions import (NotSupportedException, NotPossibleException, OutOfRangeException,
                                       MismatchException)
from ids_peak_icv.backend.utils import (create_array, execute_and_map_return_codes,
                                          check_init_for_classes_with_classmethods_only, map_point_type_to_enum,
                                          map_point_type_to_native_type,
                                          map_enum_to_point_type)
from ids_peak_icv.backend.datatypes import peak_icv_polygon_handle, peak_icv_point_type, peak_icv_point_f
from ids_peak_common.datatypes.geometry.point import Point

# Note: We loose type info here, as it is stored as a pointer to a python object
PointArray: TypeAlias = npt.NDArray[np.object_]


class Polygon:
    """
    A polygon is a two-dimensional geometric shape that is made up of a finite number of straight line
    segments connected end-to-end to form an open or closed figure.
    A polygon is represented by the points where the line segments meet.

    .. ingroup:: ids_peak_icv_python_types_geometry
    .. versionadded:: ids_peak_icv 1.1
    """

    @classmethod
    def create_from_points(cls, points: Union[PointArray, np.ndarray]) -> Polygon:
        """
        Creates an instance of Polygon using an array of Points or floats ( [[x,y],...] ).

        :param points: Array of Points or floats
        :return: Returns a polygon instance.

        :raises NotPossibleException: If the given points is not a numpy array of Points or floats.
        :raises MismatchException: If one of the coordinates in the numpy array is not a float.
        :raises OutOfRangeException: If one or more points in the numpy array are not two-dimensional.

        .. versionadded:: ids_peak_icv 1.1
        """

        size = len(points)

        point_type = None
        if size and ((hasattr(points[0], "x") and isinstance(getattr(points[0], "x"), float))
                     or isinstance(points[0][0], float)):
            point_type = peak_icv_point_f
        else:
            raise NotSupportedException("Only the point type float is supported.")

        native_type = map_point_type_to_native_type(point_type)
        c_points = create_array(point_type, size)
        for index, point in enumerate(points):
            if isinstance(point, Point) and isinstance(points, np.ndarray):
                if isinstance(point.x, native_type) and isinstance(point.y, native_type):
                    c_points[index] = point_type(point.x, point.y)
                else:
                    raise MismatchException(
                        "Both point coordinates have to be of type float.")

            elif isinstance(point, np.ndarray):
                if len(point) == 2:
                    c_points[index] = point_type(point[0], point[1])
                else:
                    raise OutOfRangeException(
                        "Point {index} has invalid length {length}".format(index=index, length=len(point)))
            else:
                raise NotPossibleException(
                    "Parameter points has to be a numpy array of Point objects or a two-dimensional numpy array.")

        handle = peak_icv_polygon_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Polygon_CreateFromPoints,
                                     ctypes.pointer(handle), c_points, size,
                                     map_point_type_to_enum(point_type).value)

        return Polygon(_handle=handle, _point_type=point_type)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create an empty Polygon create it with no arguments, in all other cases please refer to the
        classmethods.

        .. versionadded:: ids_peak_icv 1.1
        """

        self._points: PointArray | None = None
        self._handle = peak_icv_polygon_handle(None)
        self._point_type = None

        if len(args) or len(kwargs):
            self._handle = check_init_for_classes_with_classmethods_only(self.__class__.__name__,
                                                                         peak_icv_polygon_handle,
                                                                         *args, **kwargs)
            self._point_type = kwargs["_point_type"]
        else:
            polygon_handle = peak_icv_polygon_handle()
            execute_and_map_return_codes(lib_loader.dll().peak_icv_Polygon_Create,
                                         ctypes.pointer(polygon_handle))

            self._handle = polygon_handle

            c_point_type = ctypes.c_int()
            execute_and_map_return_codes(lib_loader.dll().peak_icv_Polygon_GetPointType, self._handle,
                                         ctypes.pointer(c_point_type))
            self._point_type = map_enum_to_point_type(peak_icv_point_type(c_point_type.value))

    def __getitem__(self, index: int) -> Point:
        """
        Return a point at index.

        .. versionadded:: ids_peak_icv 1.1
        """
        return cast(Point, cast(object, self.points[index]))

    @property
    def points(self) -> PointArray:
        """
        Get the points of the polygon.

        :return: List of Point objects representing the polygon's points.

        .. versionadded:: ids_peak_icv 1.1
        """
        if self._points is not None:
            return self._points

        c_num_points = ctypes.c_size_t()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Polygon_GetPoints_GetCount,
                                     self._handle, ctypes.pointer(c_num_points))

        if c_num_points.value == 0:
            self._points = np.ndarray(0)
            return cast(PointArray, self._points)

        c_points = create_array(cast(Any, self._point_type), c_num_points.value)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Polygon_GetPoints,
                                     self._handle, c_points, c_num_points.value *
                                     ctypes.sizeof(cast(ctypes.Structure, self._point_type)))

        self._points = np.array([Point(p.x, p.y) for p in c_points], dtype=Point)

        return cast(PointArray, self._points)

    @property
    def is_closed(self) -> bool:
        """
        Checks if a polygon is closed. A closed polygon contains the same point as first and last point.

        :return: True if closed, False if open.

        .. versionadded:: ids_peak_icv 1.1
        """
        is_closed = ctypes.c_bool()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Polygon_IsClosed,
                                     self._handle, ctypes.pointer(is_closed))

        return bool(is_closed.value)

    def __del__(self) -> None:
        if self._handle is not None:
            lib_loader.dll().peak_icv_Polygon_Destroy(self._handle)
