import ctypes
from enum import Enum

from ids_peak_common.datatypes import Interval, PixelFormat
from ids_peak_common.serialization import IArchive
from ids_peak_common.pipeline.modules.igain_module import IGain
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_interval_f
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.pipeline._internal.module_base import ModuleBase
from ids_peak_icv.datatypes.image import Image


class _GainType(Enum):
    MASTER = 0
    RED = 1
    GREEN = 2
    BLUE = 3


class GainModule(ModuleBase, IGain):
    """
    Gain is an image pipeline module that applies gain correction to an image.

    This module adjusts the intensity or color gain of an image by modifying
    the master and per-channel (R, G, B) gain factors. It can be used to correct
    image brightness or color balance after acquisition.

    The gain correction is applied independently to each channel, and is typically
    used as part of the early preprocessing stages of an image pipeline.

    Default configuration:
        - Master gain = 1.0
        - Red gain = 1.0
        - Green gain = 1.0
        - Blue gain = 1.0

    .. ingroup:: ids_peak_icv_python_pipeline_modules
    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_MASTER: float = 1.0
    """
    Default master gain value.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_RED: float = 1.0
    """
    Default red gain value.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_GREEN: float = 1.0
    """
    Default green gain value.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_BLUE: float = 1.0
    """
    Default blue gain value.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    SUPPORTED_PIXEL_FORMATS = [PixelFormat.BAYER_RG_8, PixelFormat.BAYER_RG_10, PixelFormat.BAYER_RG_12,
                               PixelFormat.BAYER_GR_8, PixelFormat.BAYER_GR_10, PixelFormat.BAYER_GR_12,
                               PixelFormat.BAYER_BG_8, PixelFormat.BAYER_BG_10, PixelFormat.BAYER_BG_12,
                               PixelFormat.BAYER_GB_8, PixelFormat.BAYER_GB_10, PixelFormat.BAYER_GB_12,
                               PixelFormat.MONO_8, PixelFormat.MONO_10, PixelFormat.MONO_12, PixelFormat.MONO_16]

    def __init__(self) -> None:
        """
        Creates an instance of the gain module.
        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        self._master = self.DEFAULT_MASTER
        self._red = self.DEFAULT_RED
        self._green = self.DEFAULT_GREEN
        self._blue = self.DEFAULT_BLUE

        self._handle = ctypes.c_void_p()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_Gain_Create,
            ctypes.byref(self._handle),
        )

    def __del__(self) -> None:
        if getattr(self, "_handle", None):
            lib_loader.dll().peak_icv_Preprocessing_Gain_Destroy(self._handle)

    @property
    def type(self) -> str:
        """
        Returns the type of the module for serialization purposes.
        :return: Module type.
        .. versionadded:: ids_peak_icv 1.0
        """
        return "Gain"

    def reset_to_default(self) -> None:
        """
        Resets all gain values to defaults.

        Master, Red, Green, and Blue gains are all reset to 1.0.
        .. versionadded:: ids_peak_icv 1.0
        """
        self._master = self.DEFAULT_MASTER
        self._red = self.DEFAULT_RED
        self._green = self.DEFAULT_GREEN
        self._blue = self.DEFAULT_BLUE

        self._apply(_GainType.MASTER, self._master)
        self._apply(_GainType.RED, self._red)
        self._apply(_GainType.GREEN, self._green)
        self._apply(_GainType.BLUE, self._blue)

    @property
    def master(self) -> float:
        """
        Returns the current master gain value.
        .. versionadded:: ids_peak_icv 1.0
        """
        return self._master

    @master.setter
    def master(self, value: float) -> None:
        """
        Sets the master gain.

        :param value: Gain value within the valid range returned by :py:meth:`range`.
        :raises OutOfRangeException: If value is outside the valid range.
        .. versionadded:: ids_peak_icv 1.0
        """
        self._master = value
        self._apply(_GainType.MASTER, value)

    @property
    def red(self) -> float:
        """
        Returns the current red gain value.
        .. versionadded:: ids_peak_icv 1.0
        """
        return self._red

    @red.setter
    def red(self, value: float) -> None:
        """
        Sets the red channel gain.

        :param value: Gain value within valid range.
        .. versionadded:: ids_peak_icv 1.0
        """
        self._red = value
        self._apply(_GainType.RED, value)

    @property
    def green(self) -> float:
        """
        Returns the current green gain value.
        .. versionadded:: ids_peak_icv 1.0
        """
        return self._green

    @green.setter
    def green(self, value: float) -> None:
        """
        Sets the green channel gain.

        :param value: Gain value within valid range.
        .. versionadded:: ids_peak_icv 1.0
        """
        self._green = value
        self._apply(_GainType.GREEN, value)

    @property
    def blue(self) -> float:
        """
        Returns the current blue gain value.
        .. versionadded:: ids_peak_icv 1.0
        """
        return self._blue

    @blue.setter
    def blue(self, value: float) -> None:
        """
        Sets the blue channel gain.

        :param value: Gain value within valid range.
        .. versionadded:: ids_peak_icv 1.0
        """
        self._blue = value
        self._apply(_GainType.BLUE, value)

    @property
    def range(self) -> Interval:
        """
        Returns the valid range for all gain values.

        The range applies to master and per-channel gains.

        :return: Interval representing the valid min/max gain values.
        .. versionadded:: ids_peak_icv 1.0
        """

        c_interval = peak_icv_interval_f()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_Gain_GetRange,
            self._handle,
            ctypes.pointer(c_interval)
        )
        return Interval(c_interval.minimum, c_interval.maximum)

    def process(self, input_image: Image) -> Image:
        """
        Processes the input image by applying gain correction (if enabled).

        @supportedPixelformats{Gain}

        :param input_image: Input image to be processed.
        :return: Processed output image.
        .. versionadded:: ids_peak_icv 1.0
        """
        if not self._enabled:
            return input_image

        if input_image.pixel_format not in self.SUPPORTED_PIXEL_FORMATS:
            return input_image

        input_handle = input_image._handle
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_Gain_ProcessInplace,
            self._handle,
            input_handle,
        )
        return input_image

    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the module’s internal state into an archive.

        :return: Serialized archive containing all parameters.
        .. versionadded:: ids_peak_icv 1.0
        """
        super().serialize(archive)
        archive.set("MasterGain", self.master)
        archive.set("RedGain", self.red)
        archive.set("GreenGain", self.green)
        archive.set("BlueGain", self.blue)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores the module’s state from an archive.

        :param archive: Archive containing the serialized state.
        :raises CorruptedException: If the archive is malformed.
        :raises NotSupportedException: If version is unsupported.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().deserialize(archive)

        self.master = archive.get("MasterGain", float)
        self.red = archive.get("RedGain", float)
        self.green = archive.get("GreenGain", float)
        self.blue = archive.get("BlueGain", float)

    def _apply(self, gain_type: _GainType, value: float) -> None:
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_Gain_SetValue,
            self._handle,
            ctypes.c_int(gain_type.value),
            ctypes.c_float(value),
        )

    def _fetch(self, gain_type: _GainType) -> float:
        value = ctypes.c_float()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_Gain_GetValue,
            self._handle,
            ctypes.c_int(gain_type.value),
            ctypes.pointer(value),
        )
        return value.value
