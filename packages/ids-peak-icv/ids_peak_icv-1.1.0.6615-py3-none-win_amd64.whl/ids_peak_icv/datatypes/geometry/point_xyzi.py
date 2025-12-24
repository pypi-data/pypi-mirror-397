from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

from ids_peak_icv.datatypes.geometry.point_xyz import PointXYZ


class PointXYZI(PointXYZ):
    """
    Represents a point in 3D space.

    .. ingroup:: ids_peak_icv_python_types_geometry
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, x: float, y: float, z: float, intensity: float) -> None:
        """
        Creates a point with x, y, z and intensity float channels.

        :param x: x coordinate
        :param y: y coordinate
        :param z: z coordinate
        :param intensity: intensity meta data

        .. versionadded:: ids_peak_icv 1.1
        """
        PointXYZ.__init__(self, x, y, z)
        self.intensity = intensity

    def __eq__(self, other: object) -> bool:
        """
        Check if two points of type PointXYZI are equal.

        :param other: Another PointXYZI object OR List of coordinates [x, y, z, i] OR Tuple of coordinates (x, y, z, i)

        :return: True if points are equal, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """

        if isinstance(other, PointXYZI):
            return PointXYZ.__eq__(self, other) and self.intensity == other.intensity
        if isinstance(other, list) or isinstance(other, tuple):
            if len(other) != 4:
                return False
            return bool(self.x == other[0] and self.y == other[1] and self.z == other[2] and self.intensity == other[3])

        return False

    def __ne__(self, other: object) -> bool:
        """
        Check if two points of type peak_icv_point_xyz are not equal.

        :param other: Another peak_icv_point_xyz

        :return: True if points are not equal, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """
        return not self.__eq__(other)

    def __gt__(self, other: object) -> bool:
        """
        Check if a point of type PointXYZI is greater than another point of type peak_icv_point_xyz.

        :param other: Another PointXYZI

        :return: True if point of type PointXYZI is greater than, False otherwise

        .. versionadded:: ids_peak_icv 1.1
        """

        def gt_point(x: np.float32, y: np.float32, z: np.float32, intensity: float) -> bool:
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
                    if self.z > z:
                        return True
                    elif self.z < z:
                        return False
                    else:
                        return bool(self.intensity > intensity)

        if isinstance(other, PointXYZI):
            return gt_point(other.x, other.y, other.z, other.intensity)

        if isinstance(other, list) or isinstance(other, tuple):
            if len(other) != 4:
                return False
            return gt_point(other[0], other[1], other[2], other[3])

        return False

    def __lt__(self, other: object) -> bool:
        return (not self.__gt__(other)) and self.__ne__(other)

    def __str__(self) -> str:
        """
        Get a string representation of the PointXYZI.

        :return: String representation of the PointXYZI

        .. versionadded:: ids_peak_icv 1.1
        """
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f}, {self.intensity})"
