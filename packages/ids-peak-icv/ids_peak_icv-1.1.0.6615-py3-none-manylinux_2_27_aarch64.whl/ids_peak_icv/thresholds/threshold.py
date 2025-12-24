import ctypes
from typing import Union

from ids_peak_ipl import ids_peak_ipl

from ids_peak_common.datatypes.interval import Interval

from ids_peak_icv import lib_loader
from ids_peak_icv.datatypes.region import Region
from ids_peak_icv.backend.datatypes import peak_icv_region_handle, peak_icv_interval, peak_icv_interval_f
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.exceptions import ICVException
from ids_peak_icv.datatypes.image import Image, _check_and_get_icv_image


class Threshold:
    """
    Class for thresholding an image.

    .. ingroup:: ids_peak_icv_python_thresholds
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, interval: Interval) -> None:
        """
        Creates an instance of class Threshold.

        :param interval: The interval to be used.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._interval = interval

    @property
    def interval(self) -> Interval:
        """
        Returns the interval in which the threshold will be applied.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._interval

    @interval.setter
    def interval(self, interval: Interval) -> None:
        """
        Sets the thresholding interval.

        :param interval: The interval to be used.

        :raises OutOfRangeException: If the interval is out of range.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._interval = interval

    def process(self, image: Union[Image, ids_peak_ipl.Image]) -> Region:
        """
        Applies a threshold on a given single-channel image and returns a region with selected pixels
        whose gray values are in the range Interval.minimum <= gray value <= Interval.maximum.

        :param image: An image of type Mono8, Mono10, Mono12 or Coord3D.

        :return: Region: Returns a region with selected pixels.

        :raises OutOfRangeException:    If the interval is out of bounds for the pixel format.
        :raises NotPossibleException:   If the image is too big for processing.

        .. versionadded:: ids_peak_icv 1.1
        """

        _image = _check_and_get_icv_image(image)

        image_handle = _image._handle
        region_handle = peak_icv_region_handle()

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Region_Create,
                                     ctypes.pointer(region_handle))

        try:
            c_interval: peak_icv_interval | peak_icv_interval_f

            if type(self._interval.minimum) is int:
                c_interval = peak_icv_interval(self._interval.minimum, self._interval.maximum)
            else:
                c_interval = peak_icv_interval_f(self._interval.minimum, self._interval.maximum)

            execute_and_map_return_codes(lib_loader.dll().peak_icv_Threshold_Process,
                                         image_handle,
                                         ctypes.pointer(c_interval),
                                         ctypes.sizeof(c_interval),
                                         ctypes.pointer(region_handle))
        except ICVException as e:
            lib_loader.dll().peak_icv_Region_Destroy(region_handle)
            raise e

        return Region(_handle=region_handle)

    @staticmethod
    def get_range(image: Union[Image, ids_peak_ipl.Image]) -> Interval:
        """
        Queries the minimum and maximum value of a given image and provides it as an interval.

        :param image: An image of type Mono8, Mono10, Mono12 or Coord3D.

        :return: Interval: Returns the maximum possible range of the given image.

        .. versionadded:: ids_peak_icv 1.1
        """

        _image = _check_and_get_icv_image(image)

        image_handle = _image._handle

        c_interval: peak_icv_interval | peak_icv_interval_f

        if _image._pixel_format.is_float:
            c_interval = peak_icv_interval_f()
        else:
            c_interval = peak_icv_interval()

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Threshold_GetRange,
                                     image_handle, ctypes.pointer(c_interval), ctypes.sizeof(c_interval))
        return Interval(c_interval.minimum, c_interval.maximum)
