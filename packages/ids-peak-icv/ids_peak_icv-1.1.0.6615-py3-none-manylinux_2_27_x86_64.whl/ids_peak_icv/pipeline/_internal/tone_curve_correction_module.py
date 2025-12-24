import ctypes

from ids_peak_common import PixelFormat, Interval
from ids_peak_common.serialization import IArchive
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_tone_curve_correction_handle, peak_icv_interval_f
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.pipeline._internal.module_base import ModuleBase


class ToneCurveCorrectionModule(ModuleBase):
    """
    A pipeline module for applying tone curve corrections such as gamma adjustment
    and digital black offset.

    Both, gamma and digital black corrections can be individually enabled or disabled.

    Default configuration:
    - gamma = 1.0
    - digital black = 0.0

    .. ingroup:: ids_peak_icv_python_pipeline_modules
    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_GAMMA: float = 1.0
    DEFAULT_DIGITAL_BLACK: float = 0.0

    SUPPORTED_PIXEL_FORMATS = [
        PixelFormat.MONO_8, PixelFormat.MONO_10, PixelFormat.MONO_12, PixelFormat.MONO_16, PixelFormat.RGB_8,
        PixelFormat.RGB_10, PixelFormat.RGB_12, PixelFormat.BGR_8, PixelFormat.BGR_10, PixelFormat.BGR_12,
        PixelFormat.RGBA_8, PixelFormat.RGBA_10, PixelFormat.RGBA_12,
        PixelFormat.BGRA_8, PixelFormat.BGRA_10, PixelFormat.BGRA_12
    ]

    def __init__(self) -> None:
        """
        Initialize a tone curve correction module with default settings.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        handle = peak_icv_tone_curve_correction_handle()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ToneCurveCorrection_Create,
            ctypes.pointer(handle),
        )

        self._handle = handle
        self._gamma = 1.0
        self._digital_black = 0.0
        self._gamma_enabled = True
        self._digital_black_enabled = True

    def __del__(self) -> None:
        if hasattr(self, "_handle") and self._handle:
            lib_loader.dll().peak_icv_Preprocessing_ToneCurveCorrection_Destroy(self._handle)

    @property
    def type(self) -> str:
        """
        Returns the type of the module for serialization purposes.
        :return: Module type

        .. versionadded:: ids_peak_icv 1.0
        """
        return self.__class__.__name__.replace("Module", "")

    @property
    def enabled(self) -> bool:
        """
        Get whether this module is enabled.

        When disabled, :func:`process` returns the input image unchanged.

        :return: True if the module is enabled, False otherwise.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self.digital_black_enabled or self._gamma_enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enable or disable the module.

        When disabled, :func:`process` returns the input image unchanged.

        :param value: True to enable, False to disable.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._digital_black_enabled = value
        self._gamma_enabled = value

    @property
    def gamma(self) -> float:
        """
        Gets the current gamma correction exponent.

        :return: The gamma exponent currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._gamma

    @gamma.setter
    def gamma(self, value: float) -> None:
        """
       Sets the gamma correction exponent.

       This value determines the degree of inverse gamma correction applied during processing,
       where output values are computed as pow(input, 1/gamma).
       Higher gamma values lighten the image, while values closer to zero darken it.

       .. note:: The gamma exponent must be within the valid range returned by gamma_range property.

       :param value: The gamma exponent.

       .. versionadded:: ids_peak_icv 1.0
       """
        self._gamma = value
        if self._gamma_enabled:
            self._apply_gamma(value)

    @property
    def gamma_range(self) -> Interval:
        """
        Returns the valid range for the gamma correction exponent.

        :return: An Interval containing the minimum and maximum allowed gamma values.

        .. versionadded:: ids_peak_icv 1.0
        """
        c_interval = peak_icv_interval_f()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_ToneCurveCorrection_GetGammaRange,
                                     self._handle, ctypes.pointer(c_interval))
        return Interval(c_interval.minimum, c_interval.maximum)

    @property
    def gamma_enabled(self) -> bool:
        """
        Whether gamma correction is enabled.

        :return: True if gamma is applied during processing.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._gamma_enabled

    @gamma_enabled.setter
    def gamma_enabled(self, enabled: bool) -> None:
        """
        Whether gamma correction is enabled.

        :param enabled: True if gamma correction is enabled.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._gamma_enabled = enabled
        if enabled:
            self._apply_gamma(self._gamma)

    @property
    def digital_black(self) -> float:
        """
        Gets the current digital black offset.

        :return: The digital black value currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._digital_black

    @digital_black.setter
    def digital_black(self, value: float) -> None:
        """
        Sets the digital black used for digital black correction.

        This value is subtracted from the input image channel values before gamma correction. It typically represents sensor black offset.

        \note The digital black must be within the valid range returned by digital_black_range property.

        :param value: The digital black value in normalized units.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._digital_black = value
        if self._digital_black_enabled:
            self._apply_digital_black(value)

    @property
    def digital_black_range(self) -> Interval:
        """
        Returns the valid range for the digital black correction value.

        :return: An Interval containing the minimum and maximum allowed digital black values.

        .. versionadded:: ids_peak_icv 1.0
        """
        c_interval = peak_icv_interval_f()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_ToneCurveCorrection_GetDigitalBlackRange,
                                     self._handle, ctypes.pointer(c_interval))
        return Interval(c_interval.minimum, c_interval.maximum)

    @property
    def digital_black_enabled(self) -> bool:
        """
        Whether digital black correction is enabled.

        :return: True if the digital black offset is applied.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._digital_black_enabled

    @digital_black_enabled.setter
    def digital_black_enabled(self, enabled: bool) -> None:
        """
       Whether digital black correction is enabled.

       :param enabled: True if the digital black offset is applied.

       .. versionadded:: ids_peak_icv 1.0
       """
        self._digital_black_enabled = enabled
        if enabled:
            self._apply_digital_black(self._digital_black)

    def reset_to_default(self) -> None:
        """
        Resets all module settings.

        Restores the module configuration to its default values:
        - gamma = 1.0
        - digital_black = 0.0

        .. versionadded:: ids_peak_icv 1.0
        """
        self._gamma = 1.0
        self._digital_black = 0.0
        self._apply_gamma(self._gamma)
        self._apply_digital_black(self.digital_black)

    def process(self, input_image: Image) -> Image:
        """
        Processes the input image and returns a tone curve corrected output image.

        @supportedPixelformats{ToneCurveCorrection}

        Images with other formats are passed through unmodified.

        This operation disregards any specified image regions and processes the entire image.

        :param input_image: The input image to be processed.

        :return: A new image with tone curve correction applied.

        .. versionadded:: ids_peak_icv 1.0
        """
        if not self.enabled:
            return input_image

        if input_image.pixel_format not in self.SUPPORTED_PIXEL_FORMATS:
            return input_image

        if not self.gamma_enabled and not self.digital_black_enabled:
            return input_image

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ToneCurveCorrection_ProcessInplace,
            self._handle,
            input_image._handle,
        )
        return input_image

    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the object's internal state into the provided archive.

        This function populates the given archive with all parameters required to fully represent the current state of the object.
        It ensures that the object can be reconstructed or transmitted accurately by saving all relevant data members
        in a consistent and structured format.

        :return: The serialized module's internal state.

        .. versionadded:: ids_peak_icv 1.0
        """
        # do not use base implementation, because enabled is not used in this module
        archive.set("Version", self.version)

        gamma_archive = archive.create_archive()
        gamma_archive.set("Enabled", self._gamma_enabled)
        gamma_archive.set("Value", self._gamma)
        archive.set("Gamma", gamma_archive)

        digital_black_archive = archive.create_archive()
        digital_black_archive.set("Enabled", self._digital_black_enabled)
        digital_black_archive.set("Value", self._digital_black)
        archive.set("DigitalBlack", digital_black_archive)

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
        super()._validate_version(archive)

        gamma_archive = archive.get_archive("Gamma")
        self.gamma_enabled = gamma_archive.get("Enabled", bool)
        self.gamma = float(gamma_archive.get("Value", float))

        digital_black_archive = archive.get_archive("DigitalBlack")
        self.digital_black_enabled = digital_black_archive.get("Enabled", bool)
        self.digital_black = float(digital_black_archive.get("Value", float))

    def _apply_gamma(self, value: float) -> None:
        """
        Apply gamma correction to the backend.

        .. versionadded:: ids_peak_icv 1.0
        """
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ToneCurveCorrection_SetGamma,
            self._handle,
            ctypes.c_float(value),
        )

    def _apply_digital_black(self, value: float) -> None:
        """
        Apply digital black correction to the backend.

        .. versionadded:: ids_peak_icv 1.0
        """
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ToneCurveCorrection_SetDigitalBlack,
            self._handle,
            ctypes.c_float(value),
        )
