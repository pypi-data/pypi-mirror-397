from __future__ import annotations

from ids_peak_common.datatypes.interval import Interval
from ids_peak_icv.pipeline._internal.tone_curve_correction_module import ToneCurveCorrectionModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class DigitalBlackFeature(IFeature):
    """
    Digital black applies digital black correction to an image.
    
    @supportedPixelformats{ToneCurveCorrection}

    This feature adjusts the image luminance by first subtracting a digital black and then normalizing the result.
    This compensates for sensor digital black offsets.
    The correction is applied independently to each channel in the image.
    For RGB images, it is applied to each color channel (R, G, B), and for monochrome images,
    it is applied to the single intensity channel.

    The correction is performed using the following formula::

        color_value_out = clamp((color_value_in - black) / (1.0 - black), 0.0, 1.0);

    where:

    - color_value_in is the input channel value
    - black is the digital black to be subtracted (in normalized units)
    - color_value_out is the resulting output value

    All input and output values are in the normalized range [0.0, 1.0].

    The default value for digital black is 0.0.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: ToneCurveCorrectionModule) -> None:
        """
        Creates a digital black feature for an existing tone curve correction module.
        :param module: Reference to the underlying module

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
        return self._module.digital_black_enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.digital_black_enabled = value

    def reset_to_default(self) -> None:
        """
        Resets the black level value to 0.0.

        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self.value = 0.0

    @property
    def value(self) -> float:
        """
        Gets the current black level value.
        :return: The black level value currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.digital_black

    @value.setter
    def value(self, digital_black: float) -> None:
        """
        Sets the black level value.

        This value is subtracted from the input image channel values before normalizing it.
        It typically represents sensor black offset.

        :param digital_black: A floating-point value representing the digital black value in normalized units.
        Valid values are within the range returned by range property.

        :raises OutOfRangeException: If digital black value is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.digital_black = digital_black

    @property
    def range(self) -> Interval:
        """
        Retrieves the valid range for the black level value.

        The returned interval specifies the minimum and maximum values that can be passed to value property.

        :return: An Interval representing the valid black level range.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.digital_black_range
