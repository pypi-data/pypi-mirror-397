import ctypes

from ids_peak_common.serialization import IArchive
from ids_peak_common.datatypes.pixelformat import PixelFormat
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_image_converter_handle, peak_icv_image_handle
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.pipeline._internal.module_base import ModuleBase
from ids_peak_icv.pipeline.processing_policy import ProcessingPolicy
from ids_peak_icv.datatypes.image import Image


class UnpackModule(ModuleBase):
    """
    Unpack is an image pipeline module that converts packed pixel formats into corresponding unpacked Bayer or mono formats.

    The unpack module is always enabled and cannot be disabled. It converts input images
    with packed pixel formats into their corresponding unpacked Bayer or monochrome formats,
    preserving the original bit depth of the image.

     Default configuration:
        - Target bit depth: 8
        - Processing policy: ProcessingPolicy.FAST

    .. ingroup:: ids_peak_icv_python_pipeline_modules
    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_POLICY = ProcessingPolicy.FAST
    DEFAULT_TARGET_BIT_DEPTH = 8

    def __init__(self) -> None:
        """
        Creates an instance of class UnpackModule.
        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        image_converter_handle = peak_icv_image_converter_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Create,
                                     ctypes.pointer(image_converter_handle))

        self._handle = image_converter_handle
        self._target_bit_depth: int = self.DEFAULT_TARGET_BIT_DEPTH
        self._policy: ProcessingPolicy = self.DEFAULT_POLICY

    def __del__(self) -> None:
        if hasattr(self, '_handle'):
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Destroy(self._handle)

    @property
    def target_bit_depth(self) -> int:
        """
        Get the target bit depth used during image processing.

        This value specifies the bit depth the module will aim for when unpacking
        packed pixel formats. The actual output bit depth depends on the
        selected :class:`ProcessingPolicy`.

        :return: The currently configured target bit depth.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._target_bit_depth

    @target_bit_depth.setter
    def target_bit_depth(self, bit_depth: int) -> None:
        """
        Set the target bit depth for image processing.

        The target bit depth acts as a reference when deciding how to
        unpack packed pixel formats. The actual resulting bit depth
        depends on the selected :class:`ProcessingPolicy`:

        - **Fast**:     The output bit depth is the *minimum* of the input image bit depth
                        and the target bit depth.
        - **Balanced**: The output bit depth is the *same* as the input image bit depth
                        (the target value is ignored).
        - **Enhanced**: The output bit depth is the *maximum* of the input image bit depth
                        and the target bit depth.

        This allows you to downsample, preserve, or enhance bit depth depending
        on your use case.

        :param bit_depth: The desired target bit depth (e.g., 8, 10, 12).

        .. versionadded:: ids_peak_icv 1.0
        """
        self._target_bit_depth = bit_depth

    @property
    def processing_policy(self) -> ProcessingPolicy:
        """
        Get the currently configured processing policy.
        :return: The active processing policy.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._policy

    @processing_policy.setter
    def processing_policy(self, policy: ProcessingPolicy) -> None:
        """
        Set the processing policy.
        :param policy: The desired processing policy.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._policy = policy

    @property
    def enabled(self) -> bool:
        """
        Returns true since the unpack module is always enabled.
        :return: True

        .. versionadded:: ids_peak_icv 1.0
        """
        return True

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """
        Does nothing. The module is always enabled, because otherwise following modules will fail.

        .. versionadded:: ids_peak_icv 1.0
        """
        pass

    @property
    def type(self) -> str:
        """
        Returns the type of the module for serialization purposes.
        :return: Module type

        .. versionadded:: ids_peak_icv 1.0
        """
        return "Unpack"

    def process(self, input_image: Image) -> Image:
        """
        Converts a packed pixel format image into an unpacked Bayer or monochrome format.

        This function unpacks the input image from a packed format to its corresponding
        unpacked Bayer or monochrome format, preserving the input bit depth.

        This operation disregards any specified image regions and processes the entire image.

        :param input_image: input The packed input image to unpack.
        :return: The unpacked output image with the downsampled bit depth.

        .. versionadded:: ids_peak_icv 1.0
        """
        input_bit_depth = input_image.pixel_format.storage_bits_per_channel
        output_bit_depth = self._get_output_bit_depth(input_bit_depth)
        output_pixel_format = self._get_output_pixel_format(input_image.pixel_format, output_bit_depth)

        if input_image.pixel_format == output_pixel_format:
            return input_image

        output_image_handle = peak_icv_image_handle()

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Convert, self._handle, input_image._handle,
            ctypes.c_int(output_pixel_format.value),
            ctypes.pointer(output_image_handle))

        return Image(_handle=output_image_handle)

    def reset_to_default(self) -> None:
        """
        Resets all module settings.

        Resets the target bit depth to 8 and the processing policy to ProcessingPolicy.FAST

        .. versionadded:: ids_peak_icv 1.0
        """
        self._policy = self.DEFAULT_POLICY
        self._target_bit_depth = self.DEFAULT_TARGET_BIT_DEPTH

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

    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the object's internal state into the provided archive.

        This function populates the given archive with all parameters required to fully represent the current state of the object.
        It ensures that the object can be reconstructed or transmitted accurately by saving all relevant data members
        in a consistent and structured format.

        :return: The serialized module's internal state.

        .. versionadded:: ids_peak_icv 1.0
        """
        # Unlike other modules, Unpack behaves differently: it has no version, is always enabled, and therefore cannot use the pipeline base class.
        pass

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores the object's state from the provided archive.

        This function reads and applies all necessary parameters from the given archive to reconstruct the internal state of the object.
        It ensures that the object is restored to a valid and consistent state.

        :param archive: The source archive containing the serialized parameters.

        .. note:: This function requires that the archive contains all expected fields as produced by a corresponding serialize() call.

        .. versionadded:: ids_peak_icv 1.0
        """
        # Unpack behaves differently from other modules. Since it is always enabled,
        # the archive does not need to include an "enabled" entry.
        # It also does not have a version.
        pass

    def _get_output_bit_depth(self, input_bit_depth: int) -> int:
        if self._policy == ProcessingPolicy.FAST:
            return min(input_bit_depth, self._target_bit_depth)
        elif self._policy == ProcessingPolicy.ENHANCED:
            return max(input_bit_depth, self._target_bit_depth)
        return input_bit_depth

    def _get_output_pixel_format(self, input_pixel_format: PixelFormat, output_bit_depth: int) -> PixelFormat:
        mapping = {
            # BayerBG
            PixelFormat.BAYER_BG_8: self._bayer_bg_format,
            PixelFormat.BAYER_BG_10: self._bayer_bg_format,
            PixelFormat.BAYER_BG_10_PACKED: self._bayer_bg_format,
            PixelFormat.BAYER_BG_10_GROUPED_40_IDS: self._bayer_bg_format,
            PixelFormat.BAYER_BG_12: self._bayer_bg_format,
            PixelFormat.BAYER_BG_12_PACKED: self._bayer_bg_format,
            PixelFormat.BAYER_BG_12_GROUPED_24_IDS: self._bayer_bg_format,

            # BayerGB
            PixelFormat.BAYER_GB_8: self._bayer_gb_format,
            PixelFormat.BAYER_GB_10: self._bayer_gb_format,
            PixelFormat.BAYER_GB_10_PACKED: self._bayer_gb_format,
            PixelFormat.BAYER_GB_10_GROUPED_40_IDS: self._bayer_gb_format,
            PixelFormat.BAYER_GB_12: self._bayer_gb_format,
            PixelFormat.BAYER_GB_12_PACKED: self._bayer_gb_format,
            PixelFormat.BAYER_GB_12_GROUPED_24_IDS: self._bayer_gb_format,

            # BayerGR
            PixelFormat.BAYER_GR_8: self._bayer_gr_format,
            PixelFormat.BAYER_GR_10: self._bayer_gr_format,
            PixelFormat.BAYER_GR_10_PACKED: self._bayer_gr_format,
            PixelFormat.BAYER_GR_10_GROUPED_40_IDS: self._bayer_gr_format,
            PixelFormat.BAYER_GR_12: self._bayer_gr_format,
            PixelFormat.BAYER_GR_12_PACKED: self._bayer_gr_format,
            PixelFormat.BAYER_GR_12_GROUPED_24_IDS: self._bayer_gr_format,

            # BayerRG
            PixelFormat.BAYER_RG_8: self._bayer_rg_format,
            PixelFormat.BAYER_RG_10: self._bayer_rg_format,
            PixelFormat.BAYER_RG_10_PACKED: self._bayer_rg_format,
            PixelFormat.BAYER_RG_10_GROUPED_40_IDS: self._bayer_rg_format,
            PixelFormat.BAYER_RG_12: self._bayer_rg_format,
            PixelFormat.BAYER_RG_12_PACKED: self._bayer_rg_format,
            PixelFormat.BAYER_RG_12_GROUPED_24_IDS: self._bayer_rg_format,

            # Mono
            PixelFormat.MONO_8: self._mono_format,
            PixelFormat.MONO_10: self._mono_format,
            PixelFormat.MONO_10_PACKED: self._mono_format,
            PixelFormat.MONO_10_GROUPED_40_IDS: self._mono_format,
            PixelFormat.MONO_12: self._mono_format,
            PixelFormat.MONO_12_PACKED: self._mono_format,
            PixelFormat.MONO_12_GROUPED_24_IDS: self._mono_format,

            # YUV
            PixelFormat.YUV420_8_YY_UV_SEMIPLANAR_IDS: lambda _: PixelFormat.RGB_8,
            PixelFormat.YUV420_8_YY_VU_SEMIPLANAR_IDS: lambda _: PixelFormat.RGB_8,
            PixelFormat.YUV422_8_UYVY: lambda _: PixelFormat.RGB_8,

        }

        func = mapping.get(input_pixel_format)
        if func is None:
            return input_pixel_format
        return func(output_bit_depth)

    @staticmethod
    def _bayer_bg_format(bit_depth: int) -> PixelFormat:
        if bit_depth >= 12:
            return PixelFormat.BAYER_BG_12
        elif bit_depth >= 10:
            return PixelFormat.BAYER_BG_10
        return PixelFormat.BAYER_BG_8

    @staticmethod
    def _bayer_gb_format(bit_depth: int) -> PixelFormat:
        if bit_depth >= 12:
            return PixelFormat.BAYER_GB_12
        elif bit_depth >= 10:
            return PixelFormat.BAYER_GB_10
        return PixelFormat.BAYER_GB_8

    @staticmethod
    def _bayer_gr_format(bit_depth: int) -> PixelFormat:
        if bit_depth >= 12:
            return PixelFormat.BAYER_GR_12
        elif bit_depth >= 10:
            return PixelFormat.BAYER_GR_10
        return PixelFormat.BAYER_GR_8

    @staticmethod
    def _bayer_rg_format(bit_depth: int) -> PixelFormat:
        if bit_depth >= 12:
            return PixelFormat.BAYER_RG_12
        elif bit_depth >= 10:
            return PixelFormat.BAYER_RG_10
        return PixelFormat.BAYER_RG_8

    @staticmethod
    def _mono_format(bit_depth: int) -> PixelFormat:
        if bit_depth >= 12:
            return PixelFormat.MONO_12
        elif bit_depth >= 10:
            return PixelFormat.MONO_10
        return PixelFormat.MONO_8
