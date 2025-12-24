from __future__ import annotations

from ids_peak_common.datatypes.interval import Interval
from ids_peak_icv.pipeline._internal.downsampling_module import DownsamplingModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class DecimationFeature(IFeature):
    """
    Decimation is used to decrease the image size.

    @supportedPixelformats{Downsampling}

    This method reduces resolution by selecting (i.e., skipping) pixels at regular intervals
    along columns (x), rows (y) or both.
    It is computationally efficient but may introduce aliasing.

    .. note:: Processes the entire image, ignoring any specified image region.
    .. note:: As with binning, the alpha channel of the input image (if present) is also ignored during decimation.
              It is always set to the maximum possible pixel value.
    .. note:: Decimation permanently reduces image resolution. The original resolution cannot be recovered
              after decimation is applied.

    Default Configuration:
        - x = 1
        - y = 1
        - DownsamplingMode.Decimation

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: DownsamplingModule) -> None:
        """
        Creates a DecimationFeature for an existing downsampling module.

        :param module: module Reference to the underlying DownsamplingModule.
        """

        self._module = module

    @property
    def enabled(self) -> bool:
        """
        Indicates whether the feature is currently enabled.
        :return: True if enabled; otherwise, False.
        """
        return self._module.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.
        """
        self._module.enabled = value

    def reset_to_default(self) -> None:
        """
        Resets all settings to the default configuration:
            - x = 1
            - y = 1
            - DownsamplingMode.Decimation

        .. note:: The enabled state does not change when calling this function.

        :return:
        """
        self._module.reset_to_default()

    @property
    def x(self) -> int:
        """
        Gets the current number of columns used for decimation.

        :return: The current number of columns used for decimation.
                 The decimation algorithm uses one column, skips the next x - 1 columns, and repeats this process.
        """
        return self._module.x

    @x.setter
    def x(self, value: int) -> None:
        """
        Sets the number of columns used for decimation.

        :param value: The number of columns used for decimation.
                      The decimation algorithm uses one column, skips the next x - 1 columns, and repeats this process.
                      Valid values are within the range returned by object.range.

        :raises OutOfRangeException:  If value is outside the valid range.
        """
        self._module.x = value

    @property
    def y(self) -> int:
        """
        Gets the current number of rows used for decimation.
        :return: The current number of rows used for decimation.
                 The decimation algorithm uses one row, skips the next y - 1 rows, and repeats this process.
        """
        return self._module.y

    @y.setter
    def y(self, value: int) -> None:
        """
        Sets the number of rows used for decimation.

        :param value: The number of rows used for decimation.
                      The decimation algorithm uses one row, skips the next y - 1 rows, and repeats this process.
                      Valid values are within the range returned by object.range.

        :raises OutOfRangeException:  If value is outside the valid range.
        """
        self._module.y = value

    @property
    def range(self) -> Interval:
        """
        Gets the valid range for the decimation factors x and y.

        The returned interval specifies the minimum and maximum values that can be passed to the property x or y.

        :return: An IntervalU representing the valid decimation factor range.
        """
        return self._module.range
