from __future__ import annotations

from ids_peak_common.datatypes.interval import Interval
from ids_peak_icv.pipeline._internal.tone_curve_correction_module import ToneCurveCorrectionModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class GammaFeature(IFeature):
    """
    Gamma applies an inverse gamma transformation to an image.

    @supportedPixelformats{ToneCurveCorrection}

    This module adjusts the image luminance by applying an inverse gamma correction.
    This prepares the image for a linear domain or further processing.

    The correction is applied independently to each channel in the image.
    For RGB images, it is applied to each color channel (R, G, B),
    and for monochrome images, it is applied to the single intensity channel.

    The correction is performed using the following formula: `color_value ^ (1.0 / gamma)`

    All input and output values are in the normalized range [0.0, 1.0].

    @warning Gamma values close to zero may result in very dark images,
    while very high values may cause loss of detail in dark areas.
    Use values within the range returned by range property.

    The default value for gamma is 1.0.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: ToneCurveCorrectionModule) -> None:
        """
        Creates a gamma feature for an existing tone curve correction module.
        :param module: Reference to the underlying module
        """
        self._module = module

    @property
    def enabled(self) -> bool:
        """
        Indicates whether the feature is currently enabled.
        :return: True if enabled; otherwise, False.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.gamma_enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.gamma_enabled = value

    def reset_to_default(self) -> None:
        """
        Resets the gamma value to 1.0.

        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self.value = 1.0

    @property
    def value(self) -> float:
        """
        Gets the current gamma correction exponent.
        :return: The gamma exponent currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.gamma

    @value.setter
    def value(self, gamma: float) -> None:
        """
        Sets the gamma correction exponent.

        This value determines the degree of inverse gamma correction applied during processing,
        where output values are computed as input ^ (1/gamma).
        Higher gamma values lighten the image, while values closer to zero darken it.

        :param gamma: A floating-point value representing the gamma exponent.
                     Valid values are within the range returned by range property.

        :raises OutOfRangeException: If gamma is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.gamma = gamma

    @property
    def range(self) -> Interval:
        """
        Retrieves the valid range for the gamma correction exponent.

        The returned interval specifies the minimum and maximum values that can be passed to value property.

        :return: An Interval representing the valid gamma range.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.gamma_range
