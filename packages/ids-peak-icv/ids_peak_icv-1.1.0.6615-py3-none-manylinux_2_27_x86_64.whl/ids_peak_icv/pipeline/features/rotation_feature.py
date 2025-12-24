from ids_peak_icv.datatypes.rotation_angle import Rotation
from ids_peak_icv.pipeline._internal.transformation_module import TransformationModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class RotationFeature(IFeature):
    """
    Rotation provides fixed-angle rotation functionality.

    @supportedPixelformats{ImageTransformation}

    This feature rotates images in 90-degree increments, based on the rotation mode set via the angle property.

    .. warning:: When processing images with a Bayer pattern, the result may have a different pixel format,
    though the bit depth remains unchanged. Ensure your application can handle potential pixel format changes
    after rotation.

    The default rotation is Rotation.NO_ROTATION.

    .. ingroup:: ids_peak_icv_python_pipeline_features

    .. versionadded:: ids_peak_icv 1.0
    """

    @property
    def enabled(self) -> bool:
        """
        Indicates whether the feature is currently enabled.
        :return: True if enabled; otherwise, False.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module._rotation_enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module._rotation_enabled = value

    @property
    def angle(self) -> Rotation:
        """
        Gets the current rotation angle.

        :return: The currently configured rotation angle.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.rotation_angle

    @angle.setter
    def angle(self, angle: Rotation) -> None:
        """
        Sets the desired rotation angle.

        :param angle: The rotation angle to apply (see RotationAngle enum).

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.rotation_angle = angle

    def reset_to_default(self) -> None:
        """
        Resets the rotation to Rotation.NO_ROTATION.

        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.reset_to_default()

    def __init__(self, module: TransformationModule) -> None:
        """
        Creates a RotationFeature for an existing transformation module.

        :param module: Reference to the underlying TransformationModule.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module = module
