from __future__ import annotations

import ctypes
from typing import List, Tuple, Union, TypeAlias, Callable, cast

import numpy as np
import numpy.typing as npt

from ids_peak_icv import lib_loader
from ids_peak_icv.exceptions import NotSupportedException, NotPossibleException
from ids_peak_icv.backend.datatypes import (peak_common_interval_u, peak_icv_interval_f,
                                              peak_common_rectangle_f, peak_icv_region_handle)
from ids_peak_icv.backend.utils import create_array, transform, execute_and_map_return_codes

from ids_peak_common.datatypes.interval import Interval
from ids_peak_common.datatypes.geometry.rectangle import Rectangle
from ids_peak_icv.datatypes.region import Region

# Note: We loose type info here, as it is stored as a pointer to a python object
RegionArray: TypeAlias = npt.NDArray[np.object_]


class RegionSelector:
    """
    Represents a selector for regions based on various criteria.

    .. ingroup:: ids_peak_icv_python_selectors
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, regions: RegionArray) -> None:
        """
        Creates a region selector.

        It is possible to provide an empty numpy array (no regions),
        but it does not make sense, because in this case no regions can be selected.

        :param regions: List of Region objects to select from.

        :raises NotSupportedException: If regions is not a numpy array.

        .. versionadded:: ids_peak_icv 1.1
        """

        if not isinstance(regions, np.ndarray):
            raise NotSupportedException("Parameter regions has to be a numpy array of Region objects.")

        self._regions = regions

    @property
    def regions(self) -> RegionArray:
        """
        Get the selected regions.

        :return: List[Region]: List of selected Region objects.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._regions

    def select_by_area(self, interval: Interval) -> RegionSelector:
        """
        Select regions based on their area.

        :param interval: Interval to select by. Only positive values are allowed.

        :return: RegionSelector: New RegionSelector object with selected regions.

        :raises NotSupportedException: If interval has a wrong type or the interval is not valid for this function.
        :raises NotPossibleException:  If interval has atleast one negative component.

        .. versionadded:: ids_peak_icv 1.1
        """

        if not isinstance(interval, Interval):
            raise NotSupportedException(
                "The given interval is invalid. It has to be an Interval, a Tuple(int, int) or a List "
                "with two integers")

        if interval._is_negative():
            raise NotPossibleException("The given interval is negative. You can not select a negative area.")

        c_interval = peak_common_interval_u(interval.minimum, interval.maximum)

        return self._select_by(lib_loader.dll().peak_icv_Region_SelectByArea_GetCount,
                               lib_loader.dll().peak_icv_Region_SelectByArea,
                               c_interval)

    def select_by_center_of_gravity_x(self, interval: Union[
        Interval, Tuple[float, float], List[float], Tuple[int, int], List[int]]) -> RegionSelector:
        """
        Select regions based on the center of gravity's x coordinate.

        :param interval: Interval to select by.

        :return: RegionSelector: New RegionSelector object with selected regions.

        :raises NotSupportedException: If interval has a wrong type or the interval is not valid for this function.

        .. versionadded:: ids_peak_icv 1.1
        """

        if (isinstance(interval, tuple) or isinstance(interval, list)) and len(interval) == 2:
            return self.select_by_center_of_gravity_x(Interval(interval[0], interval[1]))

        if not isinstance(interval, Interval):
            raise NotSupportedException(
                "The given interval is invalid. It has to be an Interval,"
                "a Tuple(float | int, float | int) or a List with two float | int")

        c_interval = peak_icv_interval_f(interval.minimum, interval.maximum)

        return self._select_by(lib_loader.dll().peak_icv_Region_SelectByCenterOfGravityX_GetCount,
                               lib_loader.dll().peak_icv_Region_SelectByCenterOfGravityX,
                               c_interval)

    def select_by_center_of_gravity_y(self, interval: Union[
        Interval, Tuple[float, float], List[float], Tuple[int, int], List[int]]) -> RegionSelector:
        """
        Select regions based in the center of gravity's y coordinate.

        :param interval: Interval to select by.

        :return: RegionSelector: New RegionSelector object with selected regions.

        :raises NotSupportedException: If interval has a wrong type or the interval is not valid for this function.

        .. versionadded:: ids_peak_icv 1.1
        """
        if (isinstance(interval, tuple) or isinstance(interval, list)) and len(interval) == 2:
            return self.select_by_center_of_gravity_y(Interval(interval[0], interval[1]))

        if not isinstance(interval, Interval):
            raise NotSupportedException(
                "The given interval is invalid. It has to be an Interval,"
                "a Tuple(float | int, float | int) or a List with two float | int")

        c_interval = peak_icv_interval_f(interval.minimum, interval.maximum)

        return self._select_by(lib_loader.dll().peak_icv_Region_SelectByCenterOfGravityY_GetCount,
                               lib_loader.dll().peak_icv_Region_SelectByCenterOfGravityY,
                               c_interval)

    def select_by_center_of_gravity_rect(self, rect: Union[
        Rectangle, Tuple[float, float, float, float], List[float], Tuple[int, int, int, int], List[
            int]]) -> RegionSelector:
        """
        Select regions based in the center of gravity's position within a rectangle.

        :param rect: Rectangle to select by.

        :return: RegionSelector: New RegionSelector object with selected regions.

        :raises NotSupportedException: If interval has a wrong type or the interval is not valid for this function.

        .. versionadded:: ids_peak_icv 1.1
        """

        if (isinstance(rect, tuple) or isinstance(rect, list)) and len(rect) == 4:
            return self.select_by_center_of_gravity_rect(
                Rectangle.create_from_coordinates_and_dimensions(
                    rect[0], rect[1], rect[2], rect[3]))

        if not isinstance(rect, Rectangle):
            raise NotSupportedException(
                "The given interval is invalid. It has to be an Interval,"
                "a Tuple(float | int, float | int, float | int, float | int) or a List with four float | int")

        c_rect = peak_common_rectangle_f(rect.x, rect.y, rect.width, rect.height)

        return self._select_by(lib_loader.dll().peak_icv_Region_SelectByCenterOfGravityRect_GetCount,
                               lib_loader.dll().peak_icv_Region_SelectByCenterOfGravityRect,
                               c_rect)

    def _select_by(self, select_by_get_count_function: Callable, select_by_function: Callable,
                   c_interval: ctypes.Structure) -> RegionSelector:
        if self._regions.size == 0:
            return RegionSelector(np.ndarray(0))

        handles = create_array(peak_icv_region_handle, len(self.regions))
        transform(self.regions, handles, lambda elem: elem._handle)

        c_count = ctypes.c_size_t()
        execute_and_map_return_codes(select_by_get_count_function, handles, len(handles), c_interval,
                                     ctypes.pointer(c_count))

        if c_count.value == 0:
            return RegionSelector(np.ndarray(0))

        selected_handles = create_array(peak_icv_region_handle, c_count.value)
        execute_and_map_return_codes(select_by_function, handles, len(handles), c_interval,
                                     selected_handles,
                                     len(selected_handles))

        iterable = (Region(_handle=regionHandle) for regionHandle in selected_handles)
        # workaround to fill the array on python3.7 with numpy
        selected_regions = np.empty(len(selected_handles), dtype=Region)
        for i, it in enumerate(iterable):
            selected_regions[i] = it

        return RegionSelector(cast(np.ndarray, selected_regions))
