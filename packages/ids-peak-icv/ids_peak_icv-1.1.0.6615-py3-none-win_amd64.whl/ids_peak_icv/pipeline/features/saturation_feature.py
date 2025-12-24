from __future__ import annotations

from ids_peak_common.datatypes.interval import Interval
from ids_peak_icv.pipeline._internal.color_matrix_transformation_module import ColorMatrixTransformationModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class SaturationFeature(IFeature):
    """
    Adjusts the saturation of an image by modifying a 3x3 color correction matrix.

    @supportedPixelformats{ColorMatrixTransformation}

    This feature modifies the image's color saturation by scaling the chrominance components
    of the color correction matrix. A higher saturation makes colors more vivid, while a lower
    value results in more muted tones.

    The default value for saturation is 1.0.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: ColorMatrixTransformationModule) -> None:
        """
        Creates a SaturationFeature for an existing color matrix transformation module.
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
        return self._module.saturation_enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.saturation_enabled = value

    def reset_to_default(self) -> None:
        """
        Resets the saturation value to 1.0.

        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.reset_to_default()

    @property
    def value(self) -> float:
        """
        Gets the current saturation value.
        :return: The saturation value currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.saturation

    @value.setter
    def value(self, saturation: float) -> None:
        """
        Sets the saturation value.

        :param saturation: A floating-point value representing the saturation value.
                           Valid values are within the range returned by range property.

        :raise OutOfRangeException: If saturation is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.saturation = saturation

    @property
    def range(self) -> Interval:
        """
        Retrieves the valid range for the saturation.

        The returned interval specifies the minimum and maximum values that can be passed to value property.

        :return: An Interval representing the valid saturation range.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.saturation_range
