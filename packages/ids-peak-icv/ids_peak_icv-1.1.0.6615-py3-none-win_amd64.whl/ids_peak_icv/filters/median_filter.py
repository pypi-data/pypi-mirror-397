import ctypes
from typing import Union

from ids_peak_icv import lib_loader
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image, _check_and_get_icv_image
from ids_peak_common.datatypes.geometry.size import Size
from ids_peak_ipl import ids_peak_ipl


class MedianFilter:
    """
    Class for applying a median filter to an image.

    The MedianFilter class applies a median filter to reduce noise in an image. It replaces each pixel value with the
    median value of its neighboring pixels, based on a defined kernel size.

    .. ingroup:: ids_peak_icv_python_filters
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self) -> None:
        """
        Creates an instance of the MedianFilter class with a default kernel size of 3x3.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._kernel_size = 3

    @property
    def kernel_size(self) -> int:
        """
        Gets the current kernel size used for the median filter.

        :return: int: The size of the kernel.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._kernel_size

    @kernel_size.setter
    def kernel_size(self, kernel_size: int) -> None:
        """
        Sets the size of the kernel used for the median filter.

        :param kernel_size: Size of the kernel. Must be an odd number greater than 1.
                            Also, it has to be smaller than the image size.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._kernel_size = kernel_size

    def process(self, image: Union[Image, ids_peak_ipl.Image]) -> Image:
        """
        Applies the median filter to the given image and returns the filtered result.

        This function processes the entire image and reduces noise using the specified kernel size.
        The output image will have the same pixel format and dimensions as the input image.

        .. note:: This operation disregards any specified image regions. It processes the entire image.

        :param image: The input image to which the median filter will be applied.
                      It can be of type Image or ids_peak_ipl.Image.
        :return: Image: The filtered image with reduced noise.
        :raises NotSupportedException:  If the input image is of an unsupported format.
        :raises NotPossibleException:   If the KernelSize is not a valid odd number greater than 1.
        :raises OutOfRangeException:    If the kernel size is bigger than the given image.

        .. versionadded:: ids_peak_icv 1.1
        """
        _image = _check_and_get_icv_image(image)

        output_image = Image.create_from_pixel_format_and_size(_image._pixel_format,
                                                               Size(_image.width, _image.height))

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Filter_Image_Median,
                                     _image._handle,
                                     ctypes.c_size_t(self._kernel_size),
                                     output_image._handle)

        return output_image
