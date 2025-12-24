from __future__ import annotations
import numpy as np


class PointXYZ:
    """
    Represents a point in 3D space.


    .. ingroup:: ids_peak_icv_python_types_geometry
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        """
        Creates a point with x, y and z float channels.

        :param x: x coordinate
        :param y: y coordinate
        :param z: z coordinate

        .. versionadded:: ids_peak_icv 1.1
        """
        self.x = np.float32(x)
        self.y = np.float32(y)
        self.z = np.float32(z)

    def __eq__(self, other: object) -> bool:
        """
        Check if two points of type PointXYZ are equal.

        :param other: Another PointXYZ object OR List of coordinates [x, y, z] OR Tuple of coordinates (x, y, z)

        :return: True if points are equal, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """
        from typing import cast

        if isinstance(other, PointXYZ):
            other = cast(PointXYZ, other)
            return bool(self.x == other.x and self.y == other.y and self.z == other.z)
        if isinstance(other, list) or isinstance(other, tuple):
            if len(other) != 3:
                return False
            other = cast(list | tuple, other)

            return bool(self.x == other[0] and self.y == other[1] and self.z == other[2])

        return False

    def __ne__(self, other: object) -> bool:
        """
        Check if two points of type PointXYZ are not equal.

        :param other: Another PointXYZ

        :return: True if points are not equal, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """
        return not self.__eq__(other)

    def __gt__(self, other: object) -> bool:
        """
        Check if a point of type PointXYZ is greater than another point of type PointXYZ.

        :param other: Another peak_icv_point_xyz

        :return: True if point of type PointXYZ is greater than, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """

        def gt_point(x: np.float32, y: np.float32, z: np.float32) -> bool:
            if self.x > x:
                return True
            elif self.x < x:
                return False
            else:
                if self.y > y:
                    return True
                elif self.y < y:
                    return False
                else:
                    return bool(self.z > z)

        if isinstance(other, PointXYZ):
            return gt_point(other.x, other.y, other.z)

        if isinstance(other, list) or isinstance(other, tuple):
            if len(other) != 3:
                return False
            return gt_point(other[0], other[1], other[2])

        return False

    def __lt__(self, other: object) -> bool:
        return (not self.__gt__(other)) and self.__ne__(other)

    def __str__(self) -> str:
        """
        Get a string representation of the PointXYZ.

        :return: String representation of the PointXYZ

        .. versionadded:: ids_peak_icv 1.1
        """
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
