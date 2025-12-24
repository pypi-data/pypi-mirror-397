# @package image

from __future__ import annotations

import ctypes
from typing import Any, cast
import math

import numpy as np
from ids_peak_ipl import ids_peak_ipl

from ids_peak_common.datatypes.geometry.size import Size
from ids_peak_common.datatypes.iimageview import IImageView
from ids_peak_common.datatypes.metadata import Metadata
from ids_peak_common.datatypes.pixelformat import PixelFormat, Channel

from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import (
    peak_common_size,
    peak_icv_image_handle,
    peak_icv_image_info,
    peak_icv_capture_information,
    peak_icv_binning_factor,
)
from ids_peak_icv.backend.utils import (
    execute_and_map_return_codes,
    check_init_for_classes_with_classmethods_only,
    metadata_to_capture_information,
    metadata_from_capture_information,
)
from ids_peak_icv.exceptions import OutOfRangeException

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ids_peak_icv.datatypes.region import Region


class Image:
    """
    Image Class for working with algorithms.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_types
    """

    _data: np.ndarray

    @classmethod
    def create_from_pixel_format_and_size(cls, pixel_format: PixelFormat, size: Size) -> Image:
        """
        Creates an instance of Image using a size.Size and a pixel format

        :param size: Image size in pixels
        :param pixel_format: Pixel format of the image
        :return: Returns an image instance.

        .. versionadded:: ids_peak_icv 1.0
        """

        image_handle = peak_icv_image_handle()
        image_size = peak_common_size(size.width, size.height)

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_Create,
                                     ctypes.pointer(image_handle),
                                     ctypes.c_int(pixel_format.value),
                                     image_size)

        return Image(_handle=image_handle)

    @classmethod
    def create_from_ids_peak_ipl_image(cls, ids_peak_ipl_image: ids_peak_ipl.Image) -> Image:
        """
        Creates an instance of Image using a ids_peak_ipl image.

        :param ids_peak_ipl_image: ids_peak_ipl image
        :return: Created an image instance.

        .. versionadded:: ids_peak_icv 1.0
        """
        numpy_data = (np.array(ids_peak_ipl_image.DataView(), dtype=np.uint8) if
                      ids_peak_ipl_image.PixelFormat().IsPacked() else ids_peak_ipl_image.get_numpy())
        image_info = peak_icv_image_info(
            pixel_format=ids_peak_ipl_image.PixelFormat().PixelFormatName(),
            size=peak_common_size(ids_peak_ipl_image.Width(), ids_peak_ipl_image.Height()),
            buffer_size=ids_peak_ipl_image.ByteCount(),
            buffer=numpy_data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        )
        image_handle = peak_icv_image_handle()

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_CreateFromImageInfo,
                                     ctypes.pointer(image_handle),
                                     image_info,
                                     ctypes.sizeof(image_info))
        c_capture_information = peak_icv_capture_information(binning_factor=peak_icv_binning_factor(x=1, y=1),
                                                               time_stamp=ids_peak_ipl_image.Timestamp())
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_SetCaptureInformation, image_handle,
                                     c_capture_information, ctypes.sizeof(c_capture_information))

        return cls(_handle=image_handle, _ids_peak_ipl_image=ids_peak_ipl_image)

    @classmethod
    def create_from_np_array(cls, pixel_format: PixelFormat, size: Size, data: np.ndarray) -> Image:
        """
        Creates an instance of Image using a PixelFormat, size.Size and numpy image buffer.

        :param pixel_format: Pixel format of the image
        :param size: Image size in pixels
        :param data: Numpy array holding the buffer data

        :return: Created an image instance.

        :raises OutOfRangeException: If the input array is 2D and the expected number of channels is not 1,
          or if it is 3D and the channel count does not match, or if it has a number of dimensions other than 2 or 3.

        .. versionadded:: ids_peak_icv 1.0
        """
        if data.ndim == 2:
            if pixel_format.number_of_channels != 1:
                raise OutOfRangeException("Number of channels has to be 1")
        elif data.ndim == 3:
            if data.shape[2] != pixel_format.number_of_channels:
                raise OutOfRangeException(
                    "Number of channels must be {}".format(pixel_format.number_of_channels))
        elif data.ndim == 1:
            pass
        else:
            raise OutOfRangeException("Numpy array has wrong dimension")

        image_handle = peak_icv_image_handle()
        image_info = peak_icv_image_info(
            pixel_format=pixel_format.value,
            size=peak_common_size(size.width, size.height),
            buffer_size=data.size * data.itemsize,
            buffer=data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        )

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_CreateFromImageInfo,
                                     ctypes.pointer(image_handle),
                                     image_info,
                                     ctypes.sizeof(image_info))

        return cls(_handle=image_handle, _data=data)

    @classmethod
    def create_from_file(cls, image_path: str, forced_pixel_format: PixelFormat | None = None) -> Image:
        """
        Creates an Image from a file path.

        This method loads an image from the given file path.

        If a PixelFormat is provided via ``forced_pixel_format``,
        the method attempts to interpret the file using that format.
        If interpretation fails, an exception is raised.
        Explicit conversion between image formats must be handled manually by the user.

        The following image formats are supported:

        - Bitmap (BMP)
        - Joint Photographic Experts Group (JPEG)
        - Portable Network Graphics (PNG)
        - @htmlonly Tag Image File Format (TIFF)@endhtmlonly
          (Only if ``forced_pixel_format`` is specified)
        - Raw Binary Format (RAW)

        ### Supported image and pixel formats

        #### BMP:
        @supportedPixelformats{ImageLoad_BMP}
        #### JPEG:
        @supportedPixelformats{ImageLoad_JPEG}
        #### PNG:
        @supportedPixelformats{ImageLoad_PNG}
        #### RAW:
        If ``forced_pixel_format`` is ``None`` any raw image can be loaded.

        If ``forced_pixel_format`` is specified, only the following formats are supported
        and must match the format used when saving:
        @supportedPixelformats{ImageLoad_RAW_WithPixelFormat}

        See the @ref concept_type_pixel_format for a detailed description of the pixel formats.

        :param image_path: File path on disk, pointing to an image.
        :param forced_pixel_format: Pixel format the loaded image is forced to use.
        :return: The loaded Image as a new instance

        .. versionadded:: ids_peak_icv 1.0
        """

        c_image_path = image_path.encode('utf-8')
        c_handle = peak_icv_image_handle()

        if forced_pixel_format is None:
            execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_CreateFromFile,
                                         ctypes.pointer(c_handle), ctypes.c_char_p(c_image_path))
        else:
            execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_CreateFromFileWithPixelFormat,
                                         ctypes.pointer(c_handle), ctypes.c_char_p(c_image_path),
                                         ctypes.c_int(forced_pixel_format.value))
        return cls(_handle=c_handle)

    @classmethod
    def create_from_image_view(cls, image_view: IImageView) -> Image:
        """
        Creates an instance of Image using an IImageView interface.

        :param image_view: An object implementing the IImageView interface,
                          which can be constructed from a buffer provided by a camera.
        :return: A new `Image` instance created from the given image view.

        .. versionadded:: ids_peak_icv 1.0
        """

        image = cls.create_from_np_array(image_view.pixel_format, image_view.size, image_view.to_numpy_array())
        image.metadata = image_view.metadata
        return image

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create an Image, please refer to the classmethods.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._handle = check_init_for_classes_with_classmethods_only(self.__class__.__name__,
                                                                     peak_icv_image_handle, *args, **kwargs)

        if len(kwargs):
            self._handle = kwargs["_handle"]

        image_info = peak_icv_image_info()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_GetInfo,
                                     self._handle, ctypes.pointer(image_info), ctypes.sizeof(image_info))

        self._metadata: Metadata | None = None

        self._pixel_format = PixelFormat(image_info.pixel_format)
        self._size = Size(image_info.size.width, image_info.size.height)

        num_channels = self._pixel_format.number_of_channels
        _shape = [int(self._size.height), int(self._size.width)]
        if num_channels > 1:
            _shape.append(num_channels)

        self._ids_peak_ipl_image = kwargs["_ids_peak_ipl_image"] if "_ids_peak_ipl_image" in kwargs else None

        if "_data" in kwargs:
            self._data = kwargs["_data"]
            self._raw_data = None
        else:
            packed_or_yuv = (self._pixel_format.is_packed or
                             self._pixel_format.has_channel(Channel.CHROMA_U))

            # Create a numpy array from the ctypes buffer with dtype uint8
            self._raw_data = np.ctypeslib.as_array(image_info.buffer, shape=(
                _get_byte_size(self._size,
                               self._pixel_format.allocated_bits_per_pixel,
                               packed_or_yuv),))

            if packed_or_yuv:
                self._data = self._raw_data.view(dtype=np.uint8)
            else:
                self._data = self._raw_data.view(dtype=self._pixel_format.numpy_dtype)
                self._data = self._data.reshape(_shape)

    def __del__(self) -> None:
        """
        Destructor for Image class.
        """
        if hasattr(self, '_handle'):
            lib_loader.dll().peak_icv_Image_Destroy(self._handle)

    def save(self, output_file_path: str) -> None:
        """
        Saves an instance to a file on disk. The type is specified by the given file ending in file name.

        The following image formats are supported:
        - Portable Network Graphics (PNG)
        - Bitmap (BMP)
        - Joint Photographic Experts Group (JPEG)
        - @htmlonly Tag Image File Format@endhtmlonly (TIFF)
        - Raw Binary Format (RAW)

        The compression settings for PNG and JPEG images are as follows:
        For JPEG, the image quality is set to 75%, and for PNG, the image quality is set to 100%.

        .. note:: The file extension for the given file name must match the specified image format when an image is saved.
                  Otherwise, an error will occur when saving an image. The file extensions are:
        - PNG: .png
        - BMP: .bmp
        - JPEG: .jpeg
        - TIFF: .tiff
        - RAW: .raw

        ### Supported image and pixel formats

        #### BMP:
        @supportedPixelformats{ImageSave_BMP}
        #### JPEG:
        @supportedPixelformats{ImageSave_JPEG}
        #### PNG:
        @supportedPixelformats{ImageSave_PNG}
        #### TIFF:
        @supportedPixelformats{ImageSave_TIFF}
        #### RAW:
        @supportedPixelformats{ImageSave_RAW}

        See the @ref concept_type_pixel_format for a detailed description of the pixel formats.

        :param output_file_path: The path of the file to store the image to disk.

        .. versionadded:: ids_peak_icv 1.0
        """
        c_output_file_path = output_file_path.encode('utf-8')
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_SaveToFile, self._handle,
                                     ctypes.c_char_p(c_output_file_path))

    @property
    def size(self) -> Size:
        """
        Provides the size.Size of the image.

        :return: Image size in pixels

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._size

    @property
    def width(self) -> int:
        """
        Provides the width of the image.

        :return: Image width in pixels

        .. versionadded:: ids_peak_icv 1.0
        """
        return int(self.size.width)

    @property
    def height(self) -> int:
        """
        Provides the height of the image.

        :return: Image height in pixels

        .. versionadded:: ids_peak_icv 1.0
        """
        return int(self.size.height)

    def to_numpy_array(self, copy: bool = True) -> np.ndarray:
        """
        Provides a numpy representation of the image.

        Note that the image is copied by default and the caller must not take care of the original Instance being still
        available.

        :param copy: True: The image is copied, False: The image only references the internal memory.
        :return: Image data as a numpy array. Shape is [height, width] for single channel images.
        Shape is [height, width, number of channels] for multichannel images.

        .. versionadded:: ids_peak_icv 1.0
        """

        if copy:
            return cast(np.ndarray, self._data.copy())

        return self._data

    def convert_pixel_format(self, pixel_format: PixelFormat) -> Image:
        """
        Converts the image to a different pixel format.

        If the input image has the same pixel format as the specified pixel format parameter,
        the image will be copied.

        **Restrictions**:
        - Conversion to Bayer formats is only supported from a bayer format with the same pattern,
          e.g. from BayerRG10p to BayerRG10 or BayerRG8.
        - Conversion to packed formats is not supported.
        - Conversions from RGB or BGR formats to RGBa or BGRa formats is not supported.
        - RGBa and BGRa formats support only conversions into different bit depths of the same channel layout
          or to Mono formats.
        - Confidence and Coord3D formats can only be converted to other bit depths of the same format type.

        .. note::
          For a full list of supported conversions see \ref concept_supported_pixel_format_conversion.

        :param pixel_format: The target pixel format.

        :return: A new Image with the target pixel format.

        .. versionadded:: ids_peak_icv 1.0
        """

        output_image_handle = peak_icv_image_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_Create,
                                     ctypes.pointer(output_image_handle),
                                     ctypes.c_int(pixel_format.value),
                                     peak_common_size(self._size.width, self._size.height))

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_ConvertPixelFormat,
                                     self._handle, ctypes.c_int(pixel_format.value),
                                     output_image_handle)

        return Image(_handle=output_image_handle)

    def convert_pixel_format_with_factor(self, pixel_format: PixelFormat, factor: float) -> Image:
        """
        Converts an image into another pixel format with a factor multiplied to every pixel.

        Supported conversions:
        From PixelFormat::Coord3D_C8 or PixelFormat::Coord3D_C16 to PixelFormat::Coord3D_C32f

        :param pixel_format: The target pixel format.
        :param factor: The multiplication factor.
        :return: A new instance of Image with the target pixel format.

        .. versionadded:: ids_peak_icv 1.1
        """

        output_image_handle = peak_icv_image_handle()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_Create,
                                     ctypes.pointer(output_image_handle),
                                     ctypes.c_int(pixel_format.value),
                                     peak_common_size(self._size.width, self._size.height))

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_ConvertPixelFormatWithFactor,
                                     self._handle, ctypes.c_int(pixel_format.value), ctypes.c_double(factor),
                                     output_image_handle)

        return Image(_handle=output_image_handle)

    @property
    def region(self) -> Region:
        """
        Retrieves the region.Region associated with the specified image_handle.
        :return: The image region.

        .. versionadded:: ids_peak_icv 1.0
        """
        from ids_peak_icv.datatypes.region import Region

        region = Region()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_GetRegion, self._handle,
                                     ctypes.pointer(region._handle))
        return region

    @region.setter
    def region(self, region: Region) -> None:
        """
        Updates the region.Region on the image.

        Sets a region of interest (ROI) for the specified image handle,
        which defines a sub-area of the image where operations or analyses are focused.
        Any points in the region that fall outside the bounds of the image are automatically discarded (clipped).

        :param region: The region to be set.

        .. versionadded:: ids_peak_icv 1.0
        """
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_SetRegion, self._handle,
                                     region._handle)

    def reset_region(self) -> None:
        """
        Resets the region.Region on the image to the complete image.

        .. versionadded:: ids_peak_icv 1.0
        """
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_ResetRegion, self._handle)

    @property
    def metadata(self) -> Metadata:
        """
        Retrieves the metadata.Metadata of an image which contains information about
        the image capture settings.

        :return: The metadata of the image.

        .. versionadded:: ids_peak_icv 1.0
        """

        if self._metadata is not None:
            return self._metadata

        c_capture_information = peak_icv_capture_information()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_GetCaptureInformation, self._handle,
                                     ctypes.pointer(c_capture_information), ctypes.sizeof(c_capture_information))

        self._metadata = metadata_from_capture_information(c_capture_information)
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: Metadata) -> None:
        """
        Updates the metadata.Metadata of an image which is used to store and
        manage capture settings.

        :param metadata: The metadata to be updated.

        .. versionadded:: ids_peak_icv 1.0
        """
        c_capture_information = metadata_to_capture_information(metadata, size=self._size)

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_SetCaptureInformation, self._handle,
                                     c_capture_information, ctypes.sizeof(c_capture_information))
        self._metadata = metadata_from_capture_information(c_capture_information)

    def subtract(self, subtrahend: Image) -> Image:
        """
        Subtracts the specified subtrahend image pixelwise from the current image and returns the resulting image.

        This function performs a pixelwise subtraction of the given subtrahend image from the current image.
        The resulting image is returned as a new `Image` object.
        The operation requires that both images have the same pixel format and dimensions.

        :param subtrahend: The image to subtract from the current image.
        :return: The resulting image after pixelwise subtraction.

        .. versionadded:: ids_peak_icv 1.0
        """
        difference = Image.create_from_pixel_format_and_size(self._pixel_format, self.size)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_Subtract, self._handle,
                                     subtrahend._handle, difference._handle)
        return difference

    def __sub__(self, subtrahend: Image) -> Image:
        """
       Subtracts the specified subtrahend image pixelwise from the current image and returns the resulting image.

       This function performs a pixelwise subtraction of the given subtrahend image from the current image.
       The resulting image is returned as a new `Image` object.
       The operation requires that both images have the same pixel format and dimensions.

       :param subtrahend: The image to subtract from the current image.
       :return: The resulting image after pixelwise subtraction.

       .. versionadded:: ids_peak_icv 1.0
       """
        return self.subtract(subtrahend)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Image):
            return False
        if self._handle == other._handle:
            return True
        if self.size != other.size:
            return False
        if self._pixel_format != other._pixel_format:
            return False
        if self.region != other.region:
            return False

        is_equal = ctypes.c_bool()
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_Compare, self._handle, other._handle,
                                     ctypes.pointer(is_equal))

        return is_equal.value

    @property
    def pixel_format(self) -> PixelFormat:
        return self._pixel_format


def _get_byte_size(size: Size, bits_per_pixel: int, packed_or_yuv: bool) -> int:
    """
    Calculate the byte size of an image buffer for a given size and pixel format.

    :param size: The image dimensions (width, height) in pixels.
    :param bits_per_pixel: The number of storage bits per pixel for the pixel format.
    :param packed_or_yuv: If True, assumes packed or yuv format (truncate bits to full bytes).
                   If False, assumes other format (round up to nearest byte).
    :return: The byte size of the buffer.
    """
    total_bits = int(size.width) * int(size.height) * bits_per_pixel
    if packed_or_yuv:
        return math.ceil(total_bits / 8)
    else:
        return (total_bits + 7) // 8


def _check_and_get_icv_image(image_var: Any) -> Any:
    if isinstance(image_var, ids_peak_ipl.Image):
        return Image.create_from_ids_peak_ipl_image(image_var)

    return image_var
