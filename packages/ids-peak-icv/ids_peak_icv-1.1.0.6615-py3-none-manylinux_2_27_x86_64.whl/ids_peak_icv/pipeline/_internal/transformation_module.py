import ctypes

from ids_peak_common import PixelFormat, NotSupportedException
from ids_peak_common.serialization import IArchive
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_preprocessing_transformation_parameters
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.datatypes.rotation_angle import Rotation
from ids_peak_icv.pipeline._internal import ModuleBase
from ids_peak_icv.serialization.archive import Archive


class TransformationModule(ModuleBase):
    """
    Transformation is an image pipeline module that provides mirror and rotation functionality.

    Default configuration:
        - No Rotation
        - No Mirroring

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_modules
    """

    DEFAULT_MIRROR_LEFT_RIGHT: bool = False
    DEFAULT_MIRROR_UP_DOWN: bool = False
    DEFAULT_ROTATION_ANGLE: Rotation = Rotation.NO_ROTATION

    def __init__(self) -> None:
        """
        Creates a transformation module

        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()
        self._mirror_left_right = self.DEFAULT_MIRROR_LEFT_RIGHT
        self._mirror_up_down = self.DEFAULT_MIRROR_UP_DOWN
        self._rotation_angle = self.DEFAULT_ROTATION_ANGLE
        self._rotation_enabled = True
        self._mirror_enabled = True

    @property
    def type(self) -> str:
        """
        Returns the type of the module for serialization purposes.
        :return: Module type

        .. versionadded:: ids_peak_icv 1.0
        """
        return self.__class__.__name__

    def process(self, input: Image) -> Image:
        """
        Processes the input image and returns a mirrored and/or rotated copy based on current settings.

        @supportedPixelformats{ImageTransformation}

        .. note::  When processing images with a Bayer pattern, the result may have a different pixel format,
               though the bit depth remains unchanged.

        .. note:: This operation disregards any specified image regions and processes the entire image.

        :param input: The input image to be processed.

        :return: A new image object that is the transformed result of the input.

        :raises NotSupportedException: If the image has any other than the supported pixel formats.

        .. versionadded:: ids_peak_icv 1.0
        """
        mirror_needs_processing = self._mirror_enabled and (self._mirror_left_right or self._mirror_up_down)
        rotation_needs_processing = self._rotation_enabled and self._rotation_angle != Rotation.NO_ROTATION
        if not mirror_needs_processing and not rotation_needs_processing:
            return input

        output_pixelformat = ctypes.c_uint32()
        transformation_parameters = peak_icv_preprocessing_transformation_parameters(
            self._mirror_enabled and self.mirror_left_right, self._mirror_enabled and self.mirror_up_down,
            self.rotation_angle.value if self._rotation_enabled else Rotation.NO_ROTATION.value
        )
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_Transformation_GetOutputPixelFormat,
            input.pixel_format.value,
            transformation_parameters,
            ctypes.pointer(output_pixelformat),
        )

        transpose = self._rotation_enabled and (
                self.rotation_angle == Rotation.DEGREE_90_CLOCKWISE or self.rotation_angle == Rotation.DEGREE_90_COUNTERCLOCKWISE)
        output_size = input.size.transposed() if transpose else input.size
        output_image = Image.create_from_pixel_format_and_size(PixelFormat(output_pixelformat.value), output_size)

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_Transformation_Process,
            input._handle,
            transformation_parameters,
            output_image._handle,
        )

        return output_image

    def reset_to_default(self) -> None:
        """
        Resets all settings to the default values:
            - No Rotation
            - No Mirroring

        .. versionadded:: ids_peak_icv 1.0
        """
        self._mirror_left_right = self.DEFAULT_MIRROR_LEFT_RIGHT
        self._mirror_up_down = self.DEFAULT_MIRROR_UP_DOWN
        self._rotation_angle = self.DEFAULT_ROTATION_ANGLE

    @property
    def mirror_left_right(self) -> bool:
        """
        Gets the current left-right mirroring setting.

        :return: True if left-right mirroring is enabled so that left and right will be flipped.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._mirror_left_right

    @mirror_left_right.setter
    def mirror_left_right(self, value: bool) -> None:
        """
        Sets whether the image should be mirrored left-right.

        :param value: If true, the image will be mirrored along the vertical axis.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._mirror_left_right = value

    @property
    def mirror_up_down(self) -> bool:
        """
        Gets the current up-down mirroring setting.

        :return: True if up-down mirroring is enabled so that up and down will be flipped.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._mirror_up_down

    @mirror_up_down.setter
    def mirror_up_down(self, value: bool) -> None:
        """
        Sets whether the image should be mirrored up-down.

        :param value: If true, the image will be mirrored along the horizontal axis.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._mirror_up_down = value

    @property
    def rotation_angle(self) -> Rotation:
        """
        Gets the current rotation angle.

        :return: The currently configured rotation angle.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value: Rotation) -> None:
        """
        Sets the desired rotation angle.

        :param value: The rotation angle to apply (see RotationAngle enum).

        .. versionadded:: ids_peak_icv 1.0
        """
        self._rotation_angle = value

    @property
    def enabled(self) -> bool:
        """
        Checks if the module is currently enabled.

        :return: True if the module is enabled, false otherwise.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._mirror_enabled or self._rotation_enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Sets the enabled state of this module.

        :param value: If true, the module is enabled; otherwise, it is disabled.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._mirror_enabled = value
        self._rotation_enabled = value

    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the object's internal state into an archive.

        This function populates an archive with all parameters required to fully represent the current state of the object.
        It ensures that the object can be reconstructed or transmitted accurately by saving all relevant data members
        in a consistent and structured format.

        :return: The serialized module's internal state.

        .. versionadded:: ids_peak_icv 1.0
        """
        archive.set("Version", self.version)

        mirror_archive = Archive()
        mirror_archive.set("Enabled", self._mirror_enabled)
        mirror_archive.set("LeftRight", self._mirror_left_right)
        mirror_archive.set("UpDown", self._mirror_up_down)
        archive.set("Mirror", mirror_archive)

        rotation_archive = Archive()
        rotation_archive.set("Enabled", self._rotation_enabled)
        rotation_archive.set("Angle", self._rotation_angle.value)
        archive.set("Rotation", rotation_archive)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores the object's state from the provided archive.

        This function reads and applies all necessary parameters from the given ``archive`` to reconstruct the internal
        state of the object.
        It ensures that the object is restored to a valid and consistent state.

        .. note:: This function requires that the archive contains all expected fields as produced by a
        corresponding serialize call.

        :param archive: The source archive containing the serialized parameters.

        :raises CorruptedException: If Archive is malformed, misses keys or the values are invalid
        :raises NotSupportedException: If the 'Version' entry indicates an unsupported version or if the rotation angle
        is not transformable into RotationAngle.

        .. versionadded:: ids_peak_icv 1.0
        """
        super()._validate_version(archive)

        rotation_archive = archive.get_archive("Rotation")
        self._rotation_enabled = rotation_archive.get("Enabled", bool)

        mirror_archive = archive.get_archive("Mirror")
        self._mirror_enabled = mirror_archive.get("Enabled", bool)
        self.mirror_up_down = mirror_archive.get("UpDown", bool)
        self.mirror_left_right = mirror_archive.get("LeftRight", bool)

        try:
            self.rotation_angle = Rotation(rotation_archive.get("Angle", int))
        except ValueError as e:
            raise NotSupportedException(str(e))
