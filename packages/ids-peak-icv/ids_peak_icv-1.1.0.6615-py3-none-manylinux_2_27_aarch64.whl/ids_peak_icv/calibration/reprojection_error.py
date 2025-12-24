from __future__ import annotations

from ids_peak_common.datatypes.geometry.point import Point, Vector


class ReprojectionError:
    """
    Represents the reprojection error in a calibration view.

    This structure contains details about the reprojection error for a given point in the calibration view.
    The error is described by the position, direction, and length of the error vector, providing a comprehensive
    understanding of the calibration accuracy at each point.

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, position: Point, direction: Vector, length: float) -> None:
        """
        Creates a reprojection error.

        :param position: The marker position.
        :param direction: The direction of the error.
        :param length: The magnitude of the error.

        .. versionadded:: ids_peak_icv 1.1
        """
        self.position = position
        self.direction = direction
        self.length = length
