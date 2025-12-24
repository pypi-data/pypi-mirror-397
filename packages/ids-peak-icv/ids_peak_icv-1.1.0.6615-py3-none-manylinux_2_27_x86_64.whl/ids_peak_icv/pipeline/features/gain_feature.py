from __future__ import annotations

from ids_peak_common.datatypes.interval import Interval
from ids_peak_icv.pipeline._internal import GainModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class GainFeature(IFeature):
    """
    Gain is an image pipeline feature that applies gain correction to an image.

    @supportedPixelformats{Gain}

    Gain is used to adjust pixel intensities either uniformly across all color channels using the master gain,
    or individually per channel using the red, green, and blue gains.
    With master gain, image brightness can be increased.
    With color gains, the white balance can be adjusted.
    For color images, gain is applied as follows::

        red_value_out   = red_value_in   * red_gain   * master_gain
        green_value_out = green_value_in * green_gain * master_gain
        blue_value_out  = blue_value_in  * blue_gain  * master_gain

    where red_value_in, green_value_in, and blue_value_in are the input red, green, and blue channel values, respectively,
    and red_value_out, green_value_out, and blue_value_out are the corresponding output values.
    All RGB values are normalized to the range [0.0, 1.0].
    For mono images, the color gains are ignored and applied as follows::

        gray_value_out = gray_value_in * master_gain

    where gray_value_in is the input and gray_value_out the output value, normalized to the range [0.0, 1.0].

    Warning: Excessive gain values may cause clipping and loss of image detail in bright areas.

    Default configuration:
        - Master gain = 1.0
        - Red gain = 1.0
        - Green gain = 1.0
        - Blue gain = 1.0

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: GainModule) -> None:
        """
        Creates a gain feature for an existing gain module.
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
        Resets the all gain values to 1.0.

        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.reset_to_default()

    @property
    def red(self) -> float:
        """
        Retrieves the current red gain.
        :return: The current red gain.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.red

    @red.setter
    def red(self, value: float) -> None:
        """
        Sets the red gain value.

        Sets the color gain for the red channel. The valid range for the gain value can be
        obtained using the range property.

        :param value: The red gain value to set.

        :raises OutOfRangeException:  If the gain value is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.red = value

    @property
    def green(self) -> float:
        """
        Retrieves the current green gain.
        :return: The current green gain.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.green

    @green.setter
    def green(self, value: float) -> None:
        """
        Sets the green gain value.

        Sets the color gain for the green channel. The valid range for the gain value can be
        obtained using the range property.

        :param value: The green gain value to set.

        :raises OutOfRangeException:  If the gain value is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.green = value

    @property
    def blue(self) -> float:
        """
        Retrieves the current blue gain.
        :return: The current blue gain.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.blue

    @blue.setter
    def blue(self, value: float) -> None:
        """
        Sets the blue gain value.

        Sets the color gain for the blue channel. The valid range for the gain value can be
        obtained using the range property.

        :param value: The blue gain value to set.

        :raises OutOfRangeException:  If the gain value is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.blue = value

    @property
    def master(self) -> float:
        """
        Retrieves the current master gain.
        :return: The current master gain.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.master

    @master.setter
    def master(self, value: float) -> None:
        """
        Sets the master gain value.

        Sets the color gain for the master channel. The valid range for the gain value can be
        obtained using the range property.

        :param value: The master gain value to set.

        :raises OutOfRangeException:  If the gain value is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.master = value

    @property
    def range(self) -> Interval:
        """
        Retrieves the valid range for the gamma correction exponent.

        The returned interval specifies the minimum and maximum values that can be passed to value property.

        :return: An Interval representing the valid gamma range.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.range
