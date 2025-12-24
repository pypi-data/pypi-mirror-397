import ctypes

from ids_peak_common.datatypes.pixelformat import PixelFormat
from ids_peak_common.serialization import IArchive
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import (peak_icv_image_converter_handle,
                                              peak_icv_image_handle)
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.pipeline._internal.module_base import ModuleBase


class PixelFormatConversionModule(ModuleBase):
    """
    Pixel format conversion module that transforms images to a specified output pixel format.

    This module allows explicit control over the output pixel format and provides
    serialization capabilities for saving/restoring state.

    Default pixel format: PixelFormat.RGB8

    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_OUTPUT_PIXEL_FORMAT: PixelFormat = PixelFormat.RGB_8

    def __init__(self) -> None:
        super().__init__()
        """
        Initializes a pixel format conversion module with default settings.
        
        .. versionadded:: ids_peak_icv 1.0
        """
        image_converter_handle = peak_icv_image_converter_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Create,
                                     ctypes.pointer(image_converter_handle))

        self._handle = image_converter_handle
        self._output_pixel_format = self.DEFAULT_OUTPUT_PIXEL_FORMAT
        self._enabled = True

    def __del__(self) -> None:
        if hasattr(self, '_handle'):
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Destroy(self._handle)

    @property
    def type(self) -> str:
        """
        Returns the type of the module (used for serialization or UI).

        :return: Module type.

        .. versionadded:: ids_peak_icv 1.0
        """
        return "PixelFormatConversion"

    def reset_to_default(self) -> None:
        """
        Resets the output pixel format to its default value (RGB8).

        .. versionadded:: ids_peak_icv 1.0
        """
        self._output_pixel_format = self.DEFAULT_OUTPUT_PIXEL_FORMAT

    @property
    def output_pixel_format(self) -> PixelFormat:
        """
        Returns the currently set output pixel format.

        :return: Output pixel format.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._output_pixel_format

    @output_pixel_format.setter
    def output_pixel_format(self, output_pixel_format: PixelFormat) -> None:
        """
        Sets the desired output pixel format.

        :param output_pixel_format: PixelFormat to be set as output.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._output_pixel_format = output_pixel_format

    def process(self, input_image: Image) -> Image:
        """
        Processes the input image, performing mono conversion if enabled.
        This function converts the input image to a monochrome format if the module is enabled.
        The output image preserves the bit depth of the input. If the module is disabled,
        the input image is returned unchanged.

        :param input_image: The input image to convert.
        :return: The processed image in mono format if enabled; otherwise, the original image.

        .. versionadded:: ids_peak_icv 1.0
        """

        if not self._enabled:
            return input_image

        if input_image.pixel_format == self._output_pixel_format:
            return input_image

        output_image_handle = peak_icv_image_handle()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Convert, self._handle, input_image._handle,
            ctypes.c_int(
                self._output_pixel_format.value),
            ctypes.pointer(output_image_handle))

        return Image(_handle=output_image_handle)

    def release_buffers(self) -> None:
        """
        Frees unused internal buffers.

        This module uses pre-allocated internal buffers to accelerate conversions.
        When the image size or pixel format changes, new buffers are allocated, which may cause
        the internal buffer pool to grow over time. This function can be used to release
        unused buffers and reduce memory usage.

        Avoid calling this function too frequently (e.g., after every resize or format change),
        as it introduces some overhead.

        .. versionadded:: ids_peak_icv 1.0
        """

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_ReleaseBuffers, self._handle)

    # -------------------------------------------------------------------------

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
        archive.set("OutputPixelFormat", self._output_pixel_format.string_value)

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

        self._output_pixel_format = PixelFormat.create_from_string_value(archive.get("OutputPixelFormat", str))

    # -------------------------------------------------------------------------
