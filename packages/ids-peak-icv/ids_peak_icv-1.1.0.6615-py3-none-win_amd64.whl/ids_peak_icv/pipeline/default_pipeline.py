from io import StringIO
from typing import Union, cast, Sequence

from ids_peak_common.datatypes.iimageview import IImageView
from ids_peak_common.datatypes.pixelformat import PixelFormat, Channel
from ids_peak_common.pipeline.modules.imodule import IModule
from ids_peak_common.pipeline.modules.iautofeature_module import IAutoFeature
from ids_peak_common.pipeline.pipeline_base import PipelineBase
from ids_peak_common.serialization import IArchive

from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.exceptions import (InternalErrorException, CorruptedException, NotPossibleException,
                                       NotSupportedException)
from ids_peak_icv.pipeline._internal import SharpeningModule
from ids_peak_icv.pipeline._internal.color_matrix_transformation_module import ColorMatrixTransformationModule
from ids_peak_icv.pipeline._internal.debayer_module import (DebayerModule, DebayerConversionPolicy,
                                                              DebayerChannelLayout)
from ids_peak_icv.pipeline._internal.downsampling_module import DownsamplingModule, DownsamplingMode
from ids_peak_icv.pipeline._internal.gain_module import GainModule
from ids_peak_icv.pipeline._internal.hotpixel_correction_module import HotpixelCorrectionModule
from ids_peak_icv.pipeline._internal.mono_conversion_module import MonoConversionModule
from ids_peak_icv.pipeline._internal.pixelformat_conversion_module import PixelFormatConversionModule
from ids_peak_icv.pipeline._internal.tone_curve_correction_module import ToneCurveCorrectionModule
from ids_peak_icv.pipeline._internal.transformation_module import TransformationModule
from ids_peak_icv.pipeline._internal.unpack_module import UnpackModule
from ids_peak_icv.pipeline.features import (MirrorFeature, RotationFeature,
                                              BinningFeature, DecimationFeature, GainFeature, ColorCorrectionFeature,
                                              DigitalBlackFeature, GammaFeature, HotpixelCorrectionFeature,
                                              SaturationFeature, SharpeningFeature)
from ids_peak_icv.pipeline.processing_policy import ProcessingPolicy
from ids_peak_icv.serialization.archive import Archive
from ids_peak_icv.serialization.deserializer import Deserializer
from ids_peak_icv.serialization.serializer import Serializer


class DefaultPipeline(PipelineBase):
    """
    Image processing pipeline for sequential transformation of raw image frames.

    The `Pipeline` class performs a series of configurable image processing steps on raw or pre-processed image data.
    It is designed to support a complete transformation workflow, from raw sensor input to final output format,
    with each stage modular and optionally enabled or configured.

    **Processing Steps**
    1. Unpack (Always Active) – Automatically unpacks packed sensor data formats. This stage is internal and cannot be configured.

    2. Hot Pixel Correction – Identifies and corrects defective pixels (hot pixels).

    3. Binning – Reduces resolution and improves signal-to-noise ratio by combining adjacent pixels.

    4. Decimation – Downscales the image by skipping pixels in a defined pattern.

    5. Mirror – Optionally mirrors the image left-right and/or up-down.

    6. Rotation – Rotates the image by 90, 180, or 270 degrees.

    7. Gain – Applies digital master gain to control image brightness, or digital color gains to adjust white balance.

    8. Debayer (Configured Internally) - Converts Bayer pattern raw data to RGB format and Expands monochrome images
       to RGB when a color output format is requested. This behavior is automatically determined based on the
       input and output pixel formats.

    9. ColorCorrection – Applies a color correction matrix.

    10. Auto Features – Optionally applies dynamic adjustments for example auto brightness or auto white balance.
        To enable Auto Features, an external module must be provided via::

            auto_feature_module = AutoFeatureModule(remote_device_node_map)
            pipeline.auto_feature_module = auto_feature_module

        This module is part of the **Auto Feature Library (AFL)**.

    11. Mono conversion (Configured Internally) – Converts RGB images to monochrome when a monochrome output format is requested.

    12. Sharpening – Enhances image detail using edge-based sharpening filters.

    13. Gamma – Applies gamma correction to adjust brightness and contrast.

    14. Pixel Format Conversion (Configured Internally) – Converts the processed image to the desired output pixel format.

    **Smart Pixel Format Configuration Inference**

    The pipeline includes built-in logic to automatically configure certain internal stages based on the input and
    output formats. For example:

    - If a Bayer image is provided and the output format is RGB, DebayerModule "debayering" is automatically applied.
    - If a monochrome image is input and the output format is RGB, the Debayer Module takes over the mono-to-RGB expansion.
    - If the output format is monochrome, Mono conversion is enabled.
    - If a Bayer pixel format is set as output format, the following features or modules are not processing:
      Debayer, Mono conversion, Sharpening and Gamma.
    - The Pixel Format Conversion module is responsible for converting to the specified output format.
      If necessary, the bit depth is reduced during this step.

    Use the following method to set the desired final pixel format::

        pipeline.output_pixel_format(PixelFormat.RGB_8)

    .. note:: There might be cases where some modules, even though they are enabled, do not apply their configuration,
    if the pixel format is not supported. For more information, have a look at the specific pipeline modules "process"
    methods.

    **Configuration**

    The pipeline can be configured in two ways:

    Module Access: Each configurable processing module can be accessed directly, allowing individual configuration::

        pipeline.gain.master = 1.2f
        pipeline.gamma.value = 2.2f

    Settings File: Load or save all configuration settings::

        pipeline.import_settings_from_file("config.json")
        pipeline.export_settings_to_file("config.json")

    This modular and extensible design enables flexible integration into a variety of image processing applications,
    from camera pipelines to offline image editing.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline
    """

    def __init__(self) -> None:
        """
        Initializes all internal modules to their default configuration.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._processing_policy: ProcessingPolicy = ProcessingPolicy.BALANCED
        self._unpack_module = UnpackModule()
        self._hotpixel_correction_module = HotpixelCorrectionModule()
        self._binning_module = DownsamplingModule(DownsamplingMode.BinningAverage, "Binning")
        self._decimation_module = DownsamplingModule(DownsamplingMode.Decimation, "Decimation")
        self._debayer_module = DebayerModule()
        mono_conversion_module = MonoConversionModule()
        mono_conversion_module.enabled = False
        self._mono_conversion_module = mono_conversion_module
        self._final_conversion_module = PixelFormatConversionModule()

        self._tone_curve_correction_module = ToneCurveCorrectionModule()
        self._gain_module = GainModule()
        self._color_matrix_transformation_module = ColorMatrixTransformationModule()
        self._sharpening_module = SharpeningModule()

        self._gamma_feature = GammaFeature(self._tone_curve_correction_module)
        self._digital_black_feature = DigitalBlackFeature(self._tone_curve_correction_module)
        self._gain_feature = GainFeature(self._gain_module)
        self._color_correction_feature = ColorCorrectionFeature(self._color_matrix_transformation_module)
        self._saturation_feature = SaturationFeature(self._color_matrix_transformation_module)
        self._sharpening_feature = SharpeningFeature(self._sharpening_module)
        self._hotpixel_correction_feature = HotpixelCorrectionFeature(self._hotpixel_correction_module)
        self._binning_feature = BinningFeature(self._binning_module)
        self._decimation_feature = DecimationFeature(self._decimation_module)

        self._transformation_module = TransformationModule()
        self._mirror_feature = MirrorFeature(self._transformation_module)
        self._rotation_feature = RotationFeature(self._transformation_module)

        self._auto_feature_module: None | IAutoFeature = None

    @property
    def version(self) -> int:
        """
        The pipeline version as an integer.

        .. versionadded:: ids_peak_icv 1.0
        """
        return 1

    @property
    def type(self) -> str:
        """
        The pipeline type identifier as a string, primarily used for serialization.

        .. versionadded:: ids_peak_icv 1.0
        """
        return "DefaultPipeline"

    def process(self, image: Union[Image, IImageView]) -> Image:
        """
        Applies the pipeline to the given image and returns the result as a new image.

        :param image: Input image to be processed.

        :return: Processed image result.

        .. versionadded:: ids_peak_icv 1.0
        """
        if isinstance(image, IImageView):
            return cast(Image, super().process(Image.create_from_image_view(image)))
        else:
            return cast(Image, super().process(image))

    def export_settings_to_string(self) -> str:
        """
        Converts the current pipeline settings into a string format.

        Serializes all relevant configuration parameters of the pipeline into a single string,
        which can be stored or transferred for later use.

        The export includes:
          - Pipeline version
          - Pipeline type
          - Creation timestamp (ISO UTC)
          - All module settings (type + serialized data)

        :return: A string representation of the pipeline's current configuration state.

        .. versionadded:: ids_peak_icv 1.0
        """
        from datetime import datetime, timezone

        archive = Archive({
            "Version": self.version,
            "Type": self.type,
            "Creation": datetime.now(timezone.utc).isoformat()
        })

        modules = []

        for module in self._modules:
            data_archive = Archive()
            module.serialize(data_archive)
            module_archive = Archive({
                "Type": module.type,
                "Data": data_archive
            })
            modules.append(module_archive)

        archive.set("Modules", cast(list[IArchive], modules))

        serializer = Serializer()
        buffer = StringIO()
        serializer.write(archive, buffer)

        return buffer.getvalue()

    def import_settings_from_string(self, settings: str) -> None:
        """
        Restores pipeline settings from a previously serialized string.

        Parses the provided string and applies the contained configuration values to
        update the internal state of the pipeline accordingly.

        This includes:
          - Validation of version (must be >= 1).
          - Validation of pipeline type (must match this pipeline).
          - Restoring each module's settings by invoking its `deserialize` method.

        :param settings: A string containing the serialized pipeline configuration.

        :raises CorruptedException: If the version or type is invalid.
        :raises NotPossibleException: If required module settings are missing.

        .. versionadded:: ids_peak_icv 1.0
        """

        deserializer = Deserializer()

        buffer = StringIO(settings)
        archive = deserializer.read(buffer)

        pipeline_type = archive.get("Type", str)
        if pipeline_type != self.type:
            raise NotPossibleException(
                f"The settings for {pipeline_type} are not compatible with this pipeline ({self.type})."
            )

        version = archive.get("Version", int)
        if version < self.version:
            raise NotSupportedException(
                "The given version in the settings exceeds the pipeline version. "
                f"Given settings version: {version}, pipeline version: {self.version}. "
                "The module version has to be >= the given pipeline settings version.")

        module_archives = {m.get("Type", str): m.get_archive("Data") for m in archive.get("Modules", list)}

        for module in self._modules:
            module_type = module.type
            if module_type not in module_archives:
                raise CorruptedException(
                    f"The settings for module '{module_type}' are missing!"
                )
            module.deserialize(module_archives[module_type])

    def reset_to_default(self) -> None:
        """
        Resets all modules in the pipeline to their default state. Also resets their enabled state.

        .. versionadded:: ids_peak_icv 1.0
        """
        for module in self._modules:
            module.reset_to_default()
            module.enabled = True

        self._mono_conversion_module.enabled = False

    @property
    def processing_policy(self) -> ProcessingPolicy:
        """
        The currently used processing policy.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._processing_policy

    @processing_policy.setter
    def processing_policy(self, policy: ProcessingPolicy) -> None:
        """
        Defines the processing policy for the pipeline.

        :param policy: Desired processing policy.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._processing_policy = policy
        self._unpack_module.processing_policy = policy
        self._debayer_module.processing_policy = policy

    @property
    def output_pixel_format(self) -> PixelFormat:
        """
        The current output pixel format as a `PixelFormat` enum.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._final_conversion_module.output_pixel_format

    @output_pixel_format.setter
    def output_pixel_format(self, output_pixel_format: PixelFormat) -> None:
        """
        Defines the desired pixel format for processed images.

        The pipeline will convert images to this format during processing.

        .. warning::
          When set to a Bayer format,
          the *ColorCorrection*, *Gamma* and *Sharpening* features
          will not process the image because they do not support Bayer formats.
          This may result in unexpected image quality if these features are enabled.

        :param output_pixel_format: The new pixel format as a `PixelFormat` enum.

        .. versionadded:: ids_peak_icv 1.0
        """
        is_bayer_format = output_pixel_format.is_single_channel and output_pixel_format.has_channel(Channel.BAYER)
        is_mono_format = output_pixel_format.is_single_channel and output_pixel_format.has_intensity_channel

        if is_bayer_format:
            self._debayer_module.conversion_policy = DebayerConversionPolicy.BYPASS

        elif is_mono_format:
            self._debayer_module.conversion_policy = DebayerConversionPolicy.BAYER_ONLY
            self._debayer_module.channel_layout = DebayerChannelLayout.RGB

        else:
            self._debayer_module.conversion_policy = DebayerConversionPolicy.BAYER_AND_MONO

            if self._has_rgb_channels(output_pixel_format):
                self._debayer_module.conversion_policy = DebayerConversionPolicy.BAYER_AND_MONO
                self._debayer_module.channel_layout = self._channel_layout_from_output_pixelformat(
                    output_pixel_format)

        self._mono_conversion_module.enabled = is_mono_format
        self._final_conversion_module.output_pixel_format = output_pixel_format

        bit_depth = output_pixel_format.storage_bits_per_channel

        self._unpack_module.processing_policy = self._processing_policy
        self._unpack_module.target_bit_depth = bit_depth

        self._debayer_module.processing_policy = self._processing_policy
        self._debayer_module.target_bit_depth = bit_depth

    # ------------------------------------------------------------------------------------------------------------------
    # Features
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def gamma(self) -> GammaFeature:
        """
        Provides access to the gamma feature for brightness and contrast adjustments.

        The gamma feature applies inverse gamma correction to adjust image luminance,
        preparing images for linear domain processing or display.

        :return: A reference to the gamma feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._gamma_feature

    @property
    def digital_black(self) -> DigitalBlackFeature:
        """
        Provides access to the digital black feature for sensor offset correction.

        The digital black feature compensates for sensor digital black offsets by subtracting a configurable
        black level and normalizing the result.

        :return: A reference to the digital black feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._digital_black_feature

    @property
    def gain(self) -> GainFeature:
        """
        Provides access to the gain feature for brightness and white balance adjustments.

        The gain feature allows adjustment of master gain (overall brightness) and individual
        color channel gains (red, green, blue) for white balance correction.

        :return: A reference to the gain feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._gain_feature

    @property
    def color_correction(self) -> ColorCorrectionFeature:
        """
        Provides access to the color correction feature for color space transformations.

        The color correction feature applies a 3x3 transformation matrix to perform color balancing.

        :return: A reference to the color correction feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._color_correction_feature

    @property
    def saturation(self) -> SaturationFeature:
        """
        Provides access to the saturation feature for color intensity adjustments.

        The saturation feature allows adjustment of color saturation levels, making colors more vivid
        (higher saturation) or more muted (lower saturation).

        :return: A reference to the saturation feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._saturation_feature

    @property
    def sharpening(self) -> SharpeningFeature:
        """
        Provides access to the sharpening feature for image detail enhancement.

        The sharpening feature applies edge-based sharpening filters to enhance image detail
        and improve perceived image sharpness.

        :return: A reference to the sharpening feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._sharpening_feature

    @property
    def hotpixel_correction(self) -> HotpixelCorrectionFeature:
        """
        Provides access to the hot pixel correction feature for defective pixel repair.

        The hot pixel correction feature identifies and corrects defective pixels (hot pixels)
        in camera images by replacing them with interpolated values from neighboring pixels.

        :return: A reference to the hotpixel correction feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._hotpixel_correction_feature

    @property
    def mirror(self) -> MirrorFeature:
        """
        Provides access to the mirror feature for image mirroring operations.

        The mirror feature allows horizontal (left-right) and vertical (up-down) mirroring
        of images during pipeline processing.

        :return: A reference to the mirror feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._mirror_feature

    @property
    def rotation(self) -> RotationFeature:
        """
        Provides access to the rotation feature for image rotation operations.

        The rotation feature allows rotating images in 90-degree increments (0°, 90°, 180°, 270°)
        during pipeline processing.

        :return: A reference to the rotation feature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._rotation_feature

    @property
    def binning(self) -> BinningFeature:
        """
        Provides access to the binning feature for resolution reduction and noise improvement.

        The binning feature reduces image resolution by combining adjacent pixels through
        averaging or summation, improving signal-to-noise ratio at the cost of resolution.

        :return: A reference to the BinningFeature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._binning_feature

    @property
    def decimation(self) -> DecimationFeature:
        """
         Provides access to the decimation feature for resolution reduction by pixel skipping.

         The decimation feature reduces image resolution by skipping pixels in a defined pattern,
         providing a faster alternative to binning for resolution reduction.

         A reference to the DecimationFeature.

        :return: A reference to the DecimationFeature.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._decimation_feature

    # ------------------------------------------------------------------------------------------------------------------
    # Auto Features
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def autofeature_module(self) -> IAutoFeature | None:
        """
        The used auto feature module.
        """
        return self.autofeature_module

    @autofeature_module.setter
    def autofeature_module(self, auto_feature_module: IAutoFeature | None) -> None:
        """
        Sets an auto feature module for automatic image adjustments.

        These adjustments can include features such as
        image brightness, white balance, and focus,
        depending on the capabilities of the provided module.

        .. note::
          If there is no auto feature module specified,
          this step will be skipped during processing.

        :param auto_feature_module: The auto feature module.
        """
        if self._auto_feature_module:
            self._auto_feature_module.set_gain_module(None)
        self._auto_feature_module = auto_feature_module
        self._color_matrix_transformation_module._set_autofeature_module(auto_feature_module)
        if self._auto_feature_module:
            self._auto_feature_module.set_gain_module(self._gain_module)

    # ------------------------------------------------------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def _modules(self) -> tuple[IModule, ...]:
        """
        Retrieves the sequence of processing modules for the pipeline in execution order.

        :return: Sequence of pipeline modules.

        .. versionadded:: ids_peak_icv 1.0
        """

        return (self._unpack_module, self._hotpixel_correction_module, self._binning_module, self._decimation_module,
                self._transformation_module, self._gain_module, self._debayer_module,
                self._color_matrix_transformation_module) + (
            (self._auto_feature_module,) if self._auto_feature_module is not None else ()
        ) + (self._mono_conversion_module, self._sharpening_module,
             self._tone_curve_correction_module, self._final_conversion_module)

    def _channel_layout_from_output_pixelformat(self, output_pixel_format: PixelFormat) -> DebayerChannelLayout:
        if output_pixel_format in [PixelFormat.RGB_8, PixelFormat.RGB_10, PixelFormat.RGB_12,
                                   PixelFormat.RGB_10_PACKED_32]:
            return DebayerChannelLayout.RGB

        if output_pixel_format in [PixelFormat.RGBA_8, PixelFormat.RGBA_10, PixelFormat.RGBA_12]:
            return DebayerChannelLayout.RGBA

        if output_pixel_format in [PixelFormat.BGR_8, PixelFormat.BGR_10, PixelFormat.BGR_12,
                                   PixelFormat.BGR_10_PACKED_32]:
            return DebayerChannelLayout.BGR

        if output_pixel_format in [PixelFormat.BGRA_8, PixelFormat.BGRA_10, PixelFormat.BGRA_12]:
            return DebayerChannelLayout.BGRA

        raise InternalErrorException(
            f"There is not conversion to a debayer channel layout implemented for the given pixel format. "
            f"Given pixel format: {output_pixel_format}")

    def _has_rgb_channels(self, pixel_format: PixelFormat) -> bool:
        return (pixel_format.has_channel(Channel.RED) and
                pixel_format.has_channel(Channel.GREEN) and
                pixel_format.has_channel(Channel.BLUE))
