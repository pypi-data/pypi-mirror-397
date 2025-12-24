from __future__ import annotations

from ids_peak_icv.exceptions import OutOfRangeException


class Opacity:
    """
    Class representing opacity for painting operations. Opacity indicates how much the underlying layer is hidden.

    A value of 100 means that the underlying layer is completely hidden. On the other hand, 0 means that the layer is
    completely visible.

    .. ingroup:: ids_peak_icv_python_painting
    .. versionadded:: ids_peak_icv 1.1
    """
    MINIMUM = 0
    MAXIMUM = 100

    def __init__(self, value: int = MAXIMUM) -> None:
        """
        Creates an Opacity object with a default value of 100.

        :param value: (int, optional) Value of the Opacity. Defaults to maximum.

        :raises OutOfRangeException: If the opacity value is not within the valid range.

        .. versionadded:: ids_peak_icv 1.1
        """
        if not self.MINIMUM <= value <= self.MAXIMUM:
            raise OutOfRangeException(f"Opacity value must be between {self.MINIMUM} and {self.MAXIMUM}")
        self._value = value

    @property
    def value(self) -> int:
        """
        Retrieve the current opacity.

        :return: The current opacity value.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._value

    def __eq__(self, other: object) -> bool:
        """
        Check if the Opacity object is equal to a given value.

        :param other: Value to compare with.

        :return: True if equal, False otherwise.

        .. versionadded:: ids_peak_icv 1.1
        """
        if not isinstance(other, Opacity):
            return False

        return self._value == other
