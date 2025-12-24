import ctypes

from ids_peak_common.datatypes.pixelformat import PixelFormat
from ids_peak_icv import lib_loader
from ids_peak_icv.pipeline._internal.module_base import ModuleBase
from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.backend.datatypes import peak_icv_image_converter_handle, peak_icv_image_handle
from ids_peak_icv.backend.utils import execute_and_map_return_codes


class MonoConversionModule(ModuleBase):
    """
    Mono conversion is an image pipeline module that converts images to a monochrome format.
    The mono conversion module performs a mono (grayscale) conversion on input images.
    When enabled, it converts the input image to a mono format while preserving the input bit depth.
    If disabled, the input image is passed through unchanged.

    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self) -> None:
        """
        Initializes a MonoConversionModule with default settings.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        image_converter_handle = peak_icv_image_converter_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Create,
                                     ctypes.pointer(image_converter_handle))

        self._handle = image_converter_handle

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
        return "MonoConversion"

    def reset_to_default(self) -> None:
        """
        Does nothing.

        .. versionadded:: ids_peak_icv 1.0
        """
        pass

    def process(self, input_image: Image) -> Image:
        """
        Converts the input image to the configured output pixel format.

        This operation disregards any specified image regions and processes the full image.

        :param input_image: The input image to convert.
        :return: Converted image in the configured pixel format.

        .. versionadded:: ids_peak_icv 1.0
        """

        if not self.enabled:
            return input_image

        output_pixel_format = self._get_output_format(input_image.pixel_format)
        if input_image.pixel_format == output_pixel_format:
            return input_image

        output_image_handle = peak_icv_image_handle()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Convert, self._handle, input_image._handle,
            ctypes.c_int(
                output_pixel_format.value),
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

    @staticmethod
    def _get_output_format(input_pixel_format: PixelFormat) -> PixelFormat:

        if (input_pixel_format.is_single_channel and input_pixel_format.has_intensity_channel):
            return input_pixel_format

        bit_depth = input_pixel_format.storage_bits_per_channel

        if bit_depth <= 8:
            return PixelFormat.MONO_8
        if bit_depth <= 10:
            return PixelFormat.MONO_10
        if bit_depth <= 12:
            return PixelFormat.MONO_12
        return PixelFormat.MONO_16
