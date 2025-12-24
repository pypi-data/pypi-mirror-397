from ids_peak_icv.pipeline._internal.transformation_module import TransformationModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class MirrorFeature(IFeature):
    """
    Mirror provides functionality to flip the image left-right or up-down.

    @supportedPixelformats{ImageTransformation}

    .. note:: When processing images with a Bayer pattern, the result may have a different pixel format,
    though the bit depth remains unchanged. Ensure your application can handle potential pixel format changes
    after mirroring.

    The default value is no mirroring.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    @property
    def enabled(self) -> bool:
        """
        Indicates whether the feature is currently enabled.
        :return: True if enabled; otherwise, False.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module._mirror_enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module._mirror_enabled = value

    @property
    def left_right_enabled(self) -> bool:
        """
        Gets the current left-right mirroring setting.

        :return: True if left-right mirroring is enabled so that left and right will be flipped.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.mirror_left_right

    @left_right_enabled.setter
    def left_right_enabled(self, value: bool) -> None:
        """
        Sets whether the image should be mirrored left-right.

        :param value: If true, the image will be mirrored along the vertical axis.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.mirror_left_right = value

    @property
    def up_down_enabled(self) -> bool:
        """
        Gets the current up-down mirroring setting.

        :return: True if up-down mirroring is enabled so that up and down will be flipped.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.mirror_up_down

    @up_down_enabled.setter
    def up_down_enabled(self, value: bool) -> None:
        """
        Sets whether the image should be mirrored up-down.

        :param value: If true, the image will be mirrored along the horizontal axis.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.mirror_up_down = value

    def reset_to_default(self) -> None:
        """
        Resets the mirroring to no mirroring.

        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.reset_to_default()

    def __init__(self, module: TransformationModule) -> None:
        """
        Creates a MirrorFeature for an existing transformation module.

        :param module: Reference to the underlying TransformationModule.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module = module
