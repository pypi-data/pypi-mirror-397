from __future__ import annotations

from ids_peak_common.datatypes.geometry.point import Point
from ids_peak_icv.exceptions import NotSupportedException


class CoordinateSystem:
    """
    Represents the coordinate system of a calibration view that was projected into the 2D plane.
    The coordinate system is represented by its origin and three vectors,
    each corresponding to one of the three coordinate axes (X, Y and Z).
    These vectors describe the directions of the respective axes projected from 3D into 2D space.
    Their lengths are determined by twice the distance between neighboring markers on the calibration plate.

    .. ingroup:: ids_peak_icv_python_types_geometry
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, origin: Point, x_axis: Point, y_axis: Point, z_axis: Point) -> None:
        """
        Creates a coordinate system.

        :param origin: origin coordinate
        :param x_axis: x_axis coordinate
        :param y_axis: y_axis coordinate
        :param z_axis: z_axis coordinate

        :raises NotSupportedException: if the given arguments are not points.
        .. versionadded:: ids_peak_icv 1.1
        """

        if not isinstance(origin, Point) and isinstance(x_axis, Point) and isinstance(y_axis, Point) and isinstance(
                z_axis, Point):
            raise NotSupportedException("Argument type has to be Point")

        self._origin = origin
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._z_axis = z_axis

    @property
    def origin(self) -> Point:
        """
        Origin of the coordinate system.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._origin

    @property
    def x_axis(self) -> Point:
        """
        X-axis vector of the coordinate system.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._x_axis

    @property
    def y_axis(self) -> Point:
        """
        Y-axis vector of the coordinate system.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._y_axis

    @property
    def z_axis(self) -> Point:
        """
        Z-axis vector of the coordinate system.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._z_axis

    def __eq__(self, other: object) -> bool:
        """
        Check if two coordinate systems are equal.

        :param other: Another CoordinateSystem object

        :return: True if coordinate systems are equal, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """
        if not isinstance(other, CoordinateSystem):
            return False

        return (self._origin == other.origin and self._x_axis == other.x_axis
                and self._y_axis == other.y_axis and self._z_axis == other.z_axis)

    def __ne__(self, other: object) -> bool:
        """
        Check if two coordinate systems are not equal.

        :param other: Another CoordinateSystem object

        :return: True if coordinate systems are not equal, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """
        return not self.__eq__(other)

    def __repr__(self) -> str:
        """
        Get a string representation of the CoordinateSystem.

        :return: String representation of the CoordinateSystem

        .. versionadded:: ids_peak_icv 1.1
        """
        return f"({self._origin}, {self._x_axis}, {self._y_axis}, {self._z_axis})"
