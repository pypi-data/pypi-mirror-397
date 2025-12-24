from __future__ import annotations

from ids_peak_common.datatypes.interval import Interval
from ids_peak_icv.pipeline._internal.sharpening_module import SharpeningModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class SharpeningFeature(IFeature):
    """
    Provides access to sharpening settings within an image processing pipeline.

    @supportedPixelformats{Sharpening}

    This feature emphasizes edges and fine structures by increasing contrast between adjacent pixels.
    The strength of the sharpening effect is controlled by the `value` property, where a value of 0
    applies no sharpening. Higher values increase the sharpening effect.

    Warning:
        Increasing the sharpness level can also amplify image noise and introduce visual artifacts
        such as halos around edges. Moderate values are recommended for optimal results.

    The default level for sharpening is 0.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: SharpeningModule) -> None:
        """
        Initialize the SharpeningFeature to manage the specified sharpening module.

        :param module: Reference to the underlying SharpeningModule

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
        Resets the sharpness level to its default value 0.

        .. note:: The enabled state is not changed when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.reset_to_default()

    @property
    def level(self) -> int:
        """
        Gets the current sharpness level.

        :return: The current sharpening level.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.level

    @level.setter
    def level(self, level: int) -> None:
        """
        Sets the sharpness level.

        :param level: An integer representing the desired sharpness level.
                      The acceptable range of values can be obtained from the range property.

        :raises OutOfRangeException: If the level is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.level = level

    @property
    def range(self) -> Interval:
        """
        Retrieves the valid range of sharpness levels.

        :return: An Interval object containing minimum and maximum allowed values.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.level_range
