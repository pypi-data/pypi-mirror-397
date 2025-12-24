import ctypes

from ids_peak_common.serialization import IArchive
from ids_peak_common.datatypes import Interval, PixelFormat
from ids_peak_icv import lib_loader, Image
from ids_peak_icv.backend.datatypes import peak_common_interval_u
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.pipeline._internal.module_base import ModuleBase
from ids_peak_icv.exceptions import OutOfRangeException


class SharpeningModule(ModuleBase):
    """
    Sharpening is an image pipeline module that applies a sharpening filter to enhance image detail.

    .. versionadded:: ids_peak_common 1.1
    .. ingroup:: ids_peak_icv_python_pipeline_modules
    """

    SUPPORTED_PIXEL_FORMATS = [PixelFormat.MONO_8, PixelFormat.MONO_10, PixelFormat.MONO_12,
                               PixelFormat.RGB_8, PixelFormat.RGB_10, PixelFormat.RGB_12,
                               PixelFormat.RGBA_8, PixelFormat.RGBA_10, PixelFormat.RGBA_12,
                               PixelFormat.BGR_8, PixelFormat.BGR_10, PixelFormat.BGR_12,
                               PixelFormat.BGRA_8, PixelFormat.BGRA_10, PixelFormat.BGRA_12]

    DEFAULT_LEVEL: int = 0

    _level_key = "Level"

    def __init__(self) -> None:
        """
        Creates an instance of the sharpening module.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        self._level = self.DEFAULT_LEVEL

    def __del__(self) -> None:
        pass

    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the object's internal state into the provided archive.

        This function populates the given archive with all parameters required to fully represent the current state of the object.
        It ensures that the object can be reconstructed or transmitted accurately by saving all relevant data members
        in a consistent and structured format.

        :return: The serialized module's internal state.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().serialize(archive)
        archive.set(self._level_key, self.level)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores the object's state from the provided archive.

        This function reads and applies all necessary parameters from the given archive to reconstruct the internal state of the object.
        It ensures that the object is restored to a valid and consistent state.

         :param archive: The source archive containing the serialized parameters.

        :raises CorruptedException: If Archive is malformed, misses keys or the values are invalid
        :raises NotSupportedException: If the 'Version' entry indicates an unsupported version.

        .. note:: This function requires that the archive contains all expected fields as produced by a corresponding serialize() call.

        .. versionadded:: ids_peak_icv 1.0
        """

        super().deserialize(archive)
        self.level = archive.get(self._level_key, int)

    @property
    def type(self) -> str:
        """
        Returns the type of the module for serialization purposes.
        :return: Module type

        .. versionadded:: ids_peak_icv 1.0
        """
        return self.__class__.__name__.replace("Module", "")

    def reset_to_default(self) -> None:
        """
        Resets the sharpness level to default (0).

        .. versionadded:: ids_peak_icv 1.0
        """
        self._level = self.DEFAULT_LEVEL

    @property
    def level(self) -> int:
        """
        Gets the current sharpness level.

        :return: Integer level.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._level

    @level.setter
    def level(self, level: int) -> None:
        """
        Sets the sharpness level.

        :param level: An integer specifying the sharpening strength.
        :raises OutOfRangeException: The specified level is outside the valid range.

        .. versionadded:: ids_peak_icv 1.0
        """
        range_ = self.level_range
        if level < range_.minimum or level > range_.maximum:
            raise OutOfRangeException(f"The given level value {level} is out of range!")
        self._level = level

    @property
    def level_range(self) -> Interval:
        """
        Gets the valid range of sharpening level values.

        :return: IntervalU with min and max values.

        .. versionadded:: ids_peak_icv 1.0
        """

        c_interval = peak_common_interval_u()

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_ImageFilter_Sharpening_GetRange,
            ctypes.pointer(c_interval)
        )
        return Interval(c_interval.minimum, c_interval.maximum)

    def process(self, input_image: Image) -> Image:
        """
        Apply sharpening to the specified image.

        @supportedPixelformats{Sharpening}

        If sharpening is disabled or the sharpening level is set to 0, the input
        image is returned unchanged. Otherwise, this method applies an in-place
        sharpening operation using the configured level.

        :param input_image: Input image to be processed.
        :return: Processed output image.

        .. versionadded:: ids_peak_icv 1.0
        """
        if not self._enabled or self.level == 0:
            return input_image

        if input_image.pixel_format not in self.SUPPORTED_PIXEL_FORMATS:
            return input_image

        input_handle = input_image._handle
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_ImageFilter_Sharpening_ProcessInPlace,
            input_handle,
            ctypes.c_int(self.level)
        )
        return input_image
