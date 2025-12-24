import ctypes
import enum

from ids_peak_common import Size, Interval
from ids_peak_common.serialization import IArchive

from ids_peak_icv.backend.datatypes import (peak_common_size, peak_icv_downsampling_factor,
                                              peak_icv_downsampling_handle, peak_common_interval_u)
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.exceptions import CorruptedException
from ids_peak_icv import Image, lib_loader
from ids_peak_icv.pipeline._internal import ModuleBase


class DownsamplingMode(enum.Enum):
    """
    Mode parameter for the downsampling algorithm.

    The enum holding the possible modes.

    The enum was specifically chosen to be PascalCase as the serialization across languages
    needs it to be in this specific case.

    .. ingroup:: ids_peak_icv_cpp_pipeline_modules
    .. versionadded:: ids_peak_icv 1.0
    """

    BinningAverage = 0
    """
    The averaged pixel values of neighboring rows and/or columns are computed during binning.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    BinningSum = 1
    """
    The pixel values of neighboring rows and/or columns are summed during binning.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    Decimation = 2
    """
    The additional pixel values of neighboring rows and/or columns are skipped during decimation.
    
    .. versionadded:: ids_peak_icv 1.0
    """


class DownsamplingModule(ModuleBase):
    """
     Downsampling is used to decrease the image size.

     This module provides comprehensive functionality for image downsampling,
     which is the process of reducing image resolution and dimensions.
     It supports multiple algorithms optimized for various use cases.

     There are two basic techniques for downsampling:

     - _Binning_
       This method reduces resolution by summarizing or averaging groups of pixels
       in the horizontal (x) and/or vertical (y) directions.
       It helps preserve image quality by minimizing aliasing artifacts.

     - _Decimation_
       This method reduces resolution by selecting (i.e., skipping) pixels at regular intervals
       along columns (x), rows (y) or both.
       It is computationally efficient but may introduce aliasing.

     The reduction factors are specified separately for the x (columns) and y (rows) directions.

     .. ingroup:: ids_peak_icv_python_pipeline_modules
     .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_X: int = 1
    DEFAULT_Y: int = 1

    def __init__(self, default_mode: DownsamplingMode, custom_type: str) -> None:
        """
        Creates a DownsamplingModule with @ref defaults_feature_binning "default values".

        :param default_mode: Override default mode, used when resetting the module to default
        :param custom_type: Override custom mode, used when serialized to disk

        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()
        self._x = self.DEFAULT_X
        self._y = self.DEFAULT_Y
        self._mode = default_mode
        self._default_mode = default_mode
        self._type = custom_type

        self._handle = peak_icv_downsampling_handle(None)
        handle = peak_icv_downsampling_handle()

        c_downsampling_factor = peak_icv_downsampling_factor(self._x, self._y)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_Downsampling_Create,
                                     ctypes.pointer(handle), c_downsampling_factor, self._default_mode.value)
        self._handle = handle

    def __del__(self) -> None:
        if self._handle is not None:
            lib_loader.dll().peak_icv_Preprocessing_Downsampling_Destroy(self._handle)


    @property
    def type(self) -> str:
        """
        Returns the type of the pipeline for serialization purposes.

        :return: The pipeline type identifier.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._type

    def process(self, input_image: Image) -> Image:
        """
        Applies the downsampling factors and mode to the input image and returns a downsampled copy based on current settings.

        @supportedPixelformats{Downsampling}

        .. note:: Processes the entire image, ignoring any specified image region.
        .. note:: The alpha channel of the input image (if present) is also ignored.
                  This is because the alpha channel can have different interpretations
                  — such as transparency, segmentation labels, or masks —
                  each of which would require different handling during binning.
                  Consequently, the alpha channel of the output image is always set to the maximum possible pixel value.

        :param input_image: The input image to be processed.

        :return: A new image object that is the transformed result of the input.

        :raises NotSupportedException:  If input has any other than the supported pixel formats.

        .. versionadded:: ids_peak_icv 1.0
        """
        if not self.enabled or (self.x == 1 and self.y == 1):
            return input_image

        output_size = peak_common_size()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_Downsampling_GetOutputImageSize,
                                     self._handle, input_image._handle, ctypes.pointer(output_size))

        output_image = Image.create_from_pixel_format_and_size(input_image.pixel_format,
                                                               Size(output_size.width, output_size.height))
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_Downsampling_Process,
                                     self._handle, input_image._handle, output_image._handle)
        return output_image

    def reset_to_default(self) -> None:
        """
        Resets all settings to @ref defaults_feature_binning "default values", except the custom_type, which was set
        upon creating the object.

        .. versionadded:: ids_peak_icv 1.0
        """
        self.x = self.DEFAULT_X
        self.y = self.DEFAULT_Y
        self.mode = self._default_mode

    @property
    def x(self) -> int:
        """
        Returns the current number of columns used for downsampling.

        :return: The current number of columns to downsample.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        """
        Sets the number of columns to downsample.

        :param value: The number of columns to downsample.

        .. versionadded:: ids_peak_icv 1.0
        """
        factor = peak_icv_downsampling_factor(value, self.y)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_Downsampling_SetFactor,
                                     self._handle, factor)
        self._x = value

    @property
    def y(self) -> int:
        """
        Returns the current number of rows used for downsampling.

        :return: The current number of rows to downsample.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._y

    @y.setter
    def y(self, value: int) -> None:
        """
        Sets the number of rows to downsample.

        :param value: The number of rows to downsample.

        .. versionadded:: ids_peak_icv 1.0
        """
        factor = peak_icv_downsampling_factor(self.x, value)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_Downsampling_SetFactor,
                                     self._handle, factor)
        self._y = value

    @property
    def mode(self) -> DownsamplingMode:
        """
        Returns the current DownsamplingMode.

        :return: The current DownsamplingMode.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._mode

    @mode.setter
    def mode(self, value: DownsamplingMode) -> None:
        """
        Sets the DownsamplingMode.

        :param value: The DownsamplingMode to set.

        .. versionadded:: ids_peak_icv 1.0
        """
        mode = value.value
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_Downsampling_SetMode,
                                     self._handle, mode)
        self._mode = value

    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the object's internal state into the provided archive.

        This function populates the object into an archive with all parameters required to fully represent the current state of the object.
        It ensures that the object can be reconstructed or transmitted accurately by saving all relevant data members
        in a consistent and structured format.
        :return: The serialized module's internal state.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().serialize(archive)
        archive.set("X", self.x)
        archive.set("Y", self.y)
        archive.set("Mode", self.mode.name)
        archive.set("DefaultMode", self._default_mode.name)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores the object's state from the provided archive.

        This function reads and applies all necessary parameters from the given archive to reconstruct the internal state of the object.
        It ensures that the object is restored to a valid and consistent state.

        :param archive: The source archive containing the serialized parameters.

        :raises CorruptedException: If the archive is malformed, misses keys or the values are invalid
        :raises NotSupportedException: If the 'Version' entry indicates an unsupported version.

        .. note:: This function requires that the archive contains all expected fields as produced by a corresponding serialize() call.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().deserialize(archive)

        self.x = archive.get("X", int)
        self.y = archive.get("Y", int)
        mode = archive.get("Mode", str)
        default_mode = archive.get("DefaultMode", str)

        try:
            self.mode = DownsamplingMode[mode]
            self._default_mode = DownsamplingMode[default_mode]
        except KeyError as e:
            raise CorruptedException(
                f"The given archive is corrupted. The value '{e.args[0]}' cannot be mapped to the enum DownsamplingMode.")

    @property
    def range(self) -> Interval:
        """
        Returns the valid range for downsampling factors x and y.

        :return: The valid range.

        .. versionadded:: ids_peak_icv 1.0
        """

        c_range = peak_common_interval_u()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_Downsampling_GetRange,
                                     self._handle, ctypes.pointer(c_range))

        return Interval(c_range.minimum, c_range.maximum)

