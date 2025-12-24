from ids_peak_common.datatypes.geometry import Point

from ids_peak_icv.exceptions import OutOfRangeException
from ids_peak_icv.backend.datatypes import peak_icv_binning_factor


class BinningFactor(Point):
    """
    The binning factor for the x and y directions must consist of positive integer values.
    A binning value of 2 indicates that the values of the two lines are combined into one line.

    .. versionadded:: ids_peak_icv 1.0
    @ingroup ids_peak_icv_python_types
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Creates a binning factor configuration.

        :param x: x information
        :param y: y information

        :raises OutOfRangeException: If x or y is less than or equal to zero.

        .. versionadded:: ids_peak_icv 1.0
        """
        if x < 1 or y < 1:
            raise OutOfRangeException("Given binning factor value is invalid. Value has to be bigger than 0.")
        super().__init__(x, y)

    @property
    def _c_type(self) -> peak_icv_binning_factor:
        binning_factor = peak_icv_binning_factor()
        binning_factor.x = self.x
        binning_factor.y = self.y
        return binning_factor
