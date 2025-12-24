from typing import Union

from ids_peak_icv.exceptions import NotSupportedException
from ids_peak_icv.painting.color import Color, ColorConstant, ColorPalette, ColorPaletteConstant
from ids_peak_icv.painting.drawable import IDrawable
from ids_peak_icv.painting.drawing_options import DrawingOptions
from ids_peak_icv.painting.opacity import Opacity
from ids_peak_icv.datatypes.image import Image, _check_and_get_icv_image
from ids_peak_ipl import ids_peak_ipl


class Painter:
    """
    Class for painting simple things (e.g. a region) on images.

    With the Painter, objects derived from IDrawable can be drawn in order to visualize them.
    It is possible to configure the drawing style, including color and opacity settings, for customized results.

    The Painter is initialized with the image onto which the object is to be painted. It must be of type RGB8, BGR8,
    RGBa8 or BGRa8.
    Optionally, you can configure the painter by setting the color and opacity; if omitted, default values from
    DrawingOptions are used.
    Once configured, the object to be rendered can be passed to the draw method, which paints it onto the image.
    ::
        painter = Painter(image)
        painter.color = ColorConstant.BLUE
        painter.opacity = Opacity(50)
        painter.draw(region)

    .. ingroup:: ids_peak_icv_python_painting
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, image: Union[Image, ids_peak_ipl.Image]) -> None:
        """
        Creates a Painter object.

        :param image: The image all painting operations are performed on.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._image = _check_and_get_icv_image(image)
        self._drawing_options = DrawingOptions()

    @property
    def color(self) -> Color:
        """
        Get the current color for painting.

        :return: Color: The current color.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._drawing_options.color

    @color.setter
    def color(self, color: Union[Color, ColorConstant, ColorPalette, ColorPaletteConstant]) -> None:
        """
        Set the color for painting an object into the image.

        If the draw method is called several times, there are two options:
        - the same color is used for each call,
        - the color changes with each call.

        For the first option a Color or a ColorConstant must be passed, for the second a ColorPalette or a
        ColorPaletteConstant.

        :param color: The color to set.

        :raises NotSupportedException: If color is not a Color or ColorConstant.

        .. versionadded:: ids_peak_icv 1.1
        """
        num_bits_per_pixel = self._image._pixel_format.storage_bits_per_channel
        if isinstance(color, ColorConstant):
            self._drawing_options.color = Color.create_from_constant(color, num_bits_per_pixel)
        elif isinstance(color, ColorPaletteConstant):
            self._drawing_options.color = ColorPalette.create_from_palette_constant(color, num_bits_per_pixel)
        elif isinstance(color, Color) or isinstance(color, ColorPalette):
            self._drawing_options.color = color
        else:
            raise NotSupportedException("Invalid variable given. ColorConstant or Color expected.")

    @property
    def opacity(self) -> Opacity:
        """
        Get the current opacity for painting.

        :return: Opacity: The current opacity.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._drawing_options.opacity

    @opacity.setter
    def opacity(self, opacity: Opacity) -> None:
        """
        Set the Opacity for painting.

        :param opacity: The opacity to set.

        .. versionadded:: ids_peak_icv 1.1
        """
        self._drawing_options.opacity = opacity

    def draw(self, drawable: IDrawable) -> None:
        """
        Draws the ``drawable`` onto the image, the painter was initialized with.

        For more info, please see the documentation of the specific object that shall be drawn.

        The following objects can be drawn:
            - Region

        :param drawable: The object to be drawn.

        .. versionadded:: ids_peak_icv 1.1
        """
        drawable._draw(self._image, self._drawing_options)
