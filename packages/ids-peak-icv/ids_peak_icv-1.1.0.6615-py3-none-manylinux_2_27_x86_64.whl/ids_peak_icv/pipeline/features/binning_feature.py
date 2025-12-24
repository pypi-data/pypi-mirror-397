from __future__ import annotations

import enum

from ids_peak_common.datatypes.interval import Interval

from ids_peak_icv.pipeline._internal.downsampling_module import DownsamplingModule, DownsamplingMode
from ids_peak_icv.pipeline.features.ifeature import IFeature


class BinningMode(enum.Enum):
    """
    Mode parameter for the binning algorithm.

    The enum holding the possible modes.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_types
    """

    BINNING_AVERAGE = 0
    """
    The averaged pixel values of neighboring rows and/or columns are computed during binning.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    BINNING_SUM = 1
    """
    The pixel values of neighboring rows and/or columns are summed during binning.
    
    .. versionadded:: ids_peak_icv 1.0
    """


class BinningFeature(IFeature):
    """
    Binning is used to decrease the image size.

    @supportedPixelformats{ImageTransformation}

    This method reduces resolution by summarizing or averaging groups of pixels
    in the horizontal (x) and/or vertical (y) directions.
    It helps preserve image quality by minimizing aliasing artifacts.

    .. note:: Processes the entire image, ignoring any specified image region.

    .. note:: The alpha channel of the input image (if present) is also ignored.
              This is because the alpha channel can have different interpretations
              — such as transparency, segmentation labels, or masks —
              each of which would require different handling during binning.
              Consequently, the alpha channel of the output image is always set to the maximum possible pixel value.

    .. note:: Binning permanently reduces image resolution. The original resolution cannot be recovered
              after binning is applied.

    Default configuration:
        - x = 1
        - y = 1
        - BinningMode.BinningAverage

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: DownsamplingModule) -> None:
        """
        Creates a BinningFeature for an existing downsampling module.

        :param module: Reference to the underlying DownsamplingModule.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module = module

    @property
    def enabled(self) -> bool:
        """
        Indicates whether the feature is currently enabled.
        :return: True if enabled; otherwise, False.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.enabled = value

    def reset_to_default(self) -> None:
        """
        Resets all settings to the default configuration:
            - x = 1
            - y = 1
            - BinningMode.BinningAverage

        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.reset_to_default()

    @property
    def x(self) -> int:
        """
        Gets the current number of columns used for binning.

        :return: The current number of columns summarized/averaged during binning.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.x

    @x.setter
    def x(self, value: int) -> None:
        """
        Sets the number of columns used for binning.

        :param value: An integer value representing the number of columns summarized/averaged during binning.
                      Valid values are within the range returned by object.range.
        :raises OutOfRangeException: If value is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.x = value

    @property
    def y(self) -> int:
        """
        Gets the current number of rows used for binning.

        :return: The current number of rows summarized/averaged during binning.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.y

    @y.setter
    def y(self, value: int) -> None:
        """
        Sets the number of rows used for binning.

        :param value: An integer value representing the number of rows summarized/averaged during binning.
                      Valid values are within the range returned by object.range.
        :raises OutOfRangeException: If value is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.y = value

    @property
    def mode(self) -> BinningMode:
        """
        Gets the current BinningMode.

        :return: The current BinningMode.

        .. versionadded:: ids_peak_icv 1.0
        """
        return BinningMode(self._module.mode.value)

    @mode.setter
    def mode(self, value: BinningMode) -> None:
        """
        Sets the BinningMode.

        :param value: The BinningMode to set.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.mode = DownsamplingMode(value.value)

    @property
    def range(self) -> Interval:
        """
        Gets the valid range for the binning factors x and y.

        The returned interval specifies the minimum and maximum values that can be passed to object.x or object.y.

        :return: An Interval representing the valid binning factor range.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.range
