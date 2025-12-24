import ctypes

from ids_peak_common.datatypes.pixelformat import PixelFormat, Channel
from ids_peak_common.serialization import IArchive
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_image_converter_handle, peak_icv_image_handle
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.exceptions import NotSupportedException
from ids_peak_icv.pipeline._internal.debayer_channel_layout import DebayerChannelLayout
from ids_peak_icv.pipeline._internal.debayer_conversion_policy import DebayerConversionPolicy
from ids_peak_icv.pipeline._internal.module_base import ModuleBase
from ids_peak_icv.pipeline.processing_policy import ProcessingPolicy


class DebayerModule(ModuleBase):
    """
    Debayer is an image pipeline module that converts Bayer RAW images into standard color formats.

    It performs demosaicing on Bayer-pattern RAW images, converting them into full-color images
    using configurable channel layouts such as RGB, BGR, RGBA, or BGRA. The bit depth of the output
    is inferred from the input, depending on the selected processing policy.

    Default configuration:
        - Enabled: True
        - Channel layout: DebayerChannelLayout.RGB
        - Conversion policy: DebayerConversionPolicy.BAYER_ONLY
        - Target bit depth: 8
        - Processing policy: ProcessingPolicy.FAST

    .. ingroup:: ids_peak_icv_python_pipeline_modules
    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_CHANNEL_LAYOUT: DebayerChannelLayout = DebayerChannelLayout.RGB
    DEFAULT_CONVERSION_POLICY: DebayerConversionPolicy = DebayerConversionPolicy.BAYER_ONLY
    DEFAULT_TARGET_BIT_DEPTH: int = 8
    DEFAULT_POLICY: ProcessingPolicy = ProcessingPolicy.FAST

    def __init__(self) -> None:
        """
        Creates an instance of the debayer module.
        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        image_converter_handle = peak_icv_image_converter_handle()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Create,
            ctypes.pointer(image_converter_handle)
        )

        self._handle = image_converter_handle
        self._channel_layout: DebayerChannelLayout = self.DEFAULT_CHANNEL_LAYOUT
        self._conversion_policy: DebayerConversionPolicy = self.DEFAULT_CONVERSION_POLICY
        self._target_bit_depth: int = self.DEFAULT_TARGET_BIT_DEPTH
        self._policy: ProcessingPolicy = self.DEFAULT_POLICY

    def __del__(self) -> None:
        if hasattr(self, "_handle") and self._handle:
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Destroy(self._handle)

    @property
    def type(self) -> str:
        """
        Returns the type of the module for serialization purposes.
        :return: Module type
        .. versionadded:: ids_peak_icv 1.0
        """
        return "Debayer"

    @property
    def channel_layout(self) -> DebayerChannelLayout:
        """
        Get the output channel layout used for debayered images.

        :return: The currently configured DebayerChannelLayout.
        .. versionadded:: ids_peak_icv 1.0
        """
        return self._channel_layout

    @channel_layout.setter
    def channel_layout(self, layout: DebayerChannelLayout) -> None:
        """
        Set the output channel layout for debayered images.

        This controls the order and number of color channels in the converted image.
        The bit depth is automatically inherited from the input Bayer image.

        :param layout: Desired channel layout
        .. versionadded:: ids_peak_icv 1.0
        """
        self._channel_layout = layout

    @property
    def conversion_policy(self) -> DebayerConversionPolicy:
        """
        Get the conversion policy.
        :return: The currently configured DebayerConversionPolicy.
        .. versionadded:: ids_peak_icv 1.0
        """
        return self._conversion_policy

    @conversion_policy.setter
    def conversion_policy(self, policy: DebayerConversionPolicy) -> None:
        """
        Set the debayer conversion policy.

        This policy determines which types of input images will be converted.
        All other image types are passed through unchanged.

        :param policy: Desired conversion policy.
        .. versionadded:: ids_peak_icv 1.0
        """
        self._conversion_policy = policy

    @property
    def target_bit_depth(self) -> int:
        """
        Get the target bit depth for processed images.
        :return: Target bit depth as an integer.
        .. versionadded:: ids_peak_icv 1.0
        """
        return self._target_bit_depth

    @target_bit_depth.setter
    def target_bit_depth(self, bit_depth: int) -> None:
        """
        Set the target bit depth for processed images.

        The effective output bit depth depends on the selected :class:`ProcessingPolicy`:

        - **FAST**: The minimum of input bit depth and target bit depth.
        - **BALANCED**: Equal to input bit depth.
        - **ENHANCED**: The maximum of input bit depth and target bit depth.

        :param bit_depth: Desired target bit depth (e.g., 8, 10, 12).
        .. versionadded:: ids_peak_icv 1.0
        """
        self._target_bit_depth = bit_depth

    @property
    def processing_policy(self) -> ProcessingPolicy:
        """
        Get the processing policy.
        :return: Current ProcessingPolicy value.
        .. versionadded:: ids_peak_icv 1.0
        """
        return self._policy

    @processing_policy.setter
    def processing_policy(self, policy: ProcessingPolicy) -> None:
        """
        Set the processing policy.

        The processing policy defines how the target bit depth interacts
        with the input image bit depth.

        :param policy: Desired ProcessingPolicy.
        .. versionadded:: ids_peak_icv 1.0
        """
        self._policy = policy

    def process(self, input_image: Image) -> Image:
        """
        Processes the input image by applying debayering (if enabled).

        - If the module is disabled, returns the input image unchanged.
        - If the conversion policy indicates bypass or the image format
          is not eligible, returns the input image unchanged.
        - Otherwise, converts the Bayer RAW image to the configured output format.

        :param input_image: Input image to be processed.
        :return: Processed output image.
        .. versionadded:: ids_peak_icv 1.0
        """
        if not self._enabled:
            return input_image

        input_pixel_format = input_image.pixel_format
        output_format = self._get_output_format(input_pixel_format)

        if input_pixel_format == output_format:
            return input_image

        output_handle = peak_icv_image_handle()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_Convert,
            self._handle,
            input_image._handle,
            ctypes.c_int(output_format.value),
            ctypes.pointer(output_handle)
        )
        return Image(_handle=output_handle)

    def reset_to_default(self) -> None:
        """
        Resets all module settings.

        Restores the module configuration to its default values:
          - Channel layout = RGB
          - Conversion policy = BAYER_ONLY
          - Target bit depth = 8
          - Processing policy = FAST

        .. versionadded:: ids_peak_icv 1.0
        """
        self._channel_layout = self.DEFAULT_CHANNEL_LAYOUT
        self._conversion_policy = self.DEFAULT_CONVERSION_POLICY
        self._target_bit_depth = self.DEFAULT_TARGET_BIT_DEPTH
        self._policy = self.DEFAULT_POLICY

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
            lib_loader.dll().peak_icv_Preprocessing_ImageConverter_ReleaseBuffers,
            self._handle
        )

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
        archive.set("ChannelLayout", self._channel_layout.string_value)
        archive.set("ConversionPolicy", self._conversion_policy.string_value)

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

        self._channel_layout = DebayerChannelLayout.create_from_string_value(archive.get("ChannelLayout", str))
        self._conversion_policy = DebayerConversionPolicy.create_from_string_value(
            archive.get("ConversionPolicy", str))

    # -------------------------------------------------------------------------

    def _get_output_bit_depth(self, input_bit_depth: int) -> int:
        if self._policy == ProcessingPolicy.FAST:
            return min(input_bit_depth, self._target_bit_depth)
        elif self._policy == ProcessingPolicy.ENHANCED:
            return max(input_bit_depth, self._target_bit_depth)
        return input_bit_depth

    def _get_output_format(self, input_pixel_format: PixelFormat) -> PixelFormat:
        if self._conversion_policy == DebayerConversionPolicy.BYPASS:
            return input_pixel_format

        if not input_pixel_format.is_single_channel:
            return input_pixel_format

        is_bayer = input_pixel_format.has_channel(Channel.BAYER)
        is_mono = input_pixel_format.has_channel(Channel.INTENSITY)

        if not is_bayer and (not is_mono or self._conversion_policy is not DebayerConversionPolicy.BAYER_AND_MONO):
            return input_pixel_format

        input_bit_depth = input_pixel_format.storage_bits_per_channel
        output_bit_depth = self._get_output_bit_depth(input_bit_depth)

        if output_bit_depth <= 8:
            return {
                DebayerChannelLayout.RGB: PixelFormat.RGB_8,
                DebayerChannelLayout.BGR: PixelFormat.BGR_8,
                DebayerChannelLayout.RGBA: PixelFormat.RGBA_8,
                DebayerChannelLayout.BGRA: PixelFormat.BGRA_8,
            }[self._channel_layout]

        if output_bit_depth <= 10:
            return {
                DebayerChannelLayout.RGB: PixelFormat.RGB_10,
                DebayerChannelLayout.BGR: PixelFormat.BGR_10,
                DebayerChannelLayout.RGBA: PixelFormat.RGBA_10,
                DebayerChannelLayout.BGRA: PixelFormat.BGRA_10,
            }[self._channel_layout]

        if output_bit_depth <= 12:
            return {
                DebayerChannelLayout.RGB: PixelFormat.RGB_12,
                DebayerChannelLayout.BGR: PixelFormat.BGR_12,
                DebayerChannelLayout.RGBA: PixelFormat.RGBA_12,
                DebayerChannelLayout.BGRA: PixelFormat.BGRA_12,
            }[self._channel_layout]

        raise NotSupportedException(
            f"The given input pixel format 0x{input_pixel_format.value:X} is unknown or not supported!"
        )
