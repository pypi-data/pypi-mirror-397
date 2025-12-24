from __future__ import annotations

from enum import Enum
from typing import Any

from ids_peak_icv.exceptions import OutOfRangeException, NotPossibleException, NotSupportedException


class ColorConstant(Enum):
    """
    Enum class for color constants.

    .. ingroup:: ids_peak_icv_python_painting
    .. versionadded:: ids_peak_icv 1.1
    """

    BLACK = 0
    WHITE = 1
    RED = 2
    GREEN = 3
    BLUE = 4
    DIM_GRAY = 5
    GRAY = 6
    LIGHT_GRAY = 7
    CYAN = 8
    MAGENTA = 9
    YELLOW = 10
    MEDIUM_SLATE_BLUE = 11
    CORAL = 12
    SLATE_BLUE = 13
    SPRING_GREEN = 14
    ORANGE_RED = 15
    DARK_OLIVE_GREEN = 16
    PINK = 17
    CADET_BLUE = 18
    GOLDENROD = 19
    ORANGE = 20
    GOLD = 21
    FOREST_GREEN = 22
    CORNFLOWER_BLUE = 23
    NAVY = 24
    TURQUOISE = 25
    DARK_SLATE_BLUE = 26
    LIGHT_BLUE = 27
    INDIAN_RED = 28
    VIOLET_RED = 29
    LIGHT_STEEL_BLUE = 30
    MEDIUM_BLUE = 31
    KHAKI = 32
    VIOLET = 33
    FIREBRICK = 34
    MIDNIGHT_BLUE = 35


class ColorPaletteConstant(Enum):
    """
    Enum class for color palette constants.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_painting
    """

    COLORED_3 = 0
    """
    3 color palette (red, green, blue)
    
    .. versionadded:: ids_peak_icv 1.0
    """

    COLORED_6 = 1
    """
    6 color palette (red, green, blue, yellow, magenta, cyan)
    
    .. versionadded:: ids_peak_icv 1.0
    """


class Color:
    """
    Class holding color codes.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_painting
    """

    @classmethod
    def create_from_rgb(cls, red: int, green: int, blue: int, num_bits_per_pixel: int = 8) -> Color:
        """
        Creates a color from red, green and blue values.

        The values must be between 0 and 255 and will be automatically adapted to the given bit range.

        :param red: Red value.
        :param green: Green value.
        :param blue: Blue value.
        :param num_bits_per_pixel: Number of bits per pixel. Defaults to 8.

        :raises OutOfRangeException: If the color values are out of range.

        :return: A Color object.

        .. versionadded:: ids_peak_icv 1.0
        """

        if not 0 <= red <= 255 or not 0 <= green <= 255 or not 0 <= blue <= 255:
            raise OutOfRangeException("Color values must be between 0 and 255.")

        red = red * ((1 << num_bits_per_pixel) - 1) // 255
        green = green * ((1 << num_bits_per_pixel) - 1) // 255
        blue = blue * ((1 << num_bits_per_pixel) - 1) // 255

        color_code = (red << 32) + (green << 16) + blue

        return Color(_color_code=color_code)

    @classmethod
    def create_from_constant(cls, color_constant: ColorConstant, num_bits_per_pixel: int) -> Color:
        """
        Creates a color from a color constant value.

        :param color_constant: A ColorConstant.
        :param num_bits_per_pixel: Number of bits per pixel.

        :raises NotSupportedException: If the color constant is unknown.

        :return: A Color object.

        .. versionadded:: ids_peak_icv 1.0
        """

        if color_constant == ColorConstant.BLACK:
            return Color.create_from_rgb(0, 0, 0, num_bits_per_pixel)
        elif color_constant == ColorConstant.WHITE:
            return Color.create_from_rgb(255, 255, 255, num_bits_per_pixel)
        elif color_constant == ColorConstant.RED:
            return Color.create_from_rgb(255, 0, 0, num_bits_per_pixel)
        elif color_constant == ColorConstant.GREEN:
            return Color.create_from_rgb(0, 255, 0, num_bits_per_pixel)
        elif color_constant == ColorConstant.BLUE:
            return Color.create_from_rgb(0, 0, 255, num_bits_per_pixel)
        elif color_constant == ColorConstant.DIM_GRAY:
            return Color.create_from_rgb(105, 105, 105, num_bits_per_pixel)
        elif color_constant == ColorConstant.GRAY:
            return Color.create_from_rgb(128, 128, 128, num_bits_per_pixel)
        elif color_constant == ColorConstant.LIGHT_GRAY:
            return Color.create_from_rgb(211, 211, 211, num_bits_per_pixel)
        elif color_constant == ColorConstant.CYAN:
            return Color.create_from_rgb(0, 255, 255, num_bits_per_pixel)
        elif color_constant == ColorConstant.MAGENTA:
            return Color.create_from_rgb(255, 0, 255, num_bits_per_pixel)
        elif color_constant == ColorConstant.YELLOW:
            return Color.create_from_rgb(255, 255, 0, num_bits_per_pixel)
        elif color_constant == ColorConstant.MEDIUM_SLATE_BLUE:
            return Color.create_from_rgb(123, 104, 238, num_bits_per_pixel)
        elif color_constant == ColorConstant.CORAL:
            return Color.create_from_rgb(255, 127, 80, num_bits_per_pixel)
        elif color_constant == ColorConstant.SLATE_BLUE:
            return Color.create_from_rgb(106, 90, 205, num_bits_per_pixel)
        elif color_constant == ColorConstant.SPRING_GREEN:
            return Color.create_from_rgb(0, 255, 127, num_bits_per_pixel)
        elif color_constant == ColorConstant.ORANGE_RED:
            return Color.create_from_rgb(255, 69, 0, num_bits_per_pixel)
        elif color_constant == ColorConstant.DARK_OLIVE_GREEN:
            return Color.create_from_rgb(85, 107, 47, num_bits_per_pixel)
        elif color_constant == ColorConstant.PINK:
            return Color.create_from_rgb(255, 192, 203, num_bits_per_pixel)
        elif color_constant == ColorConstant.CADET_BLUE:
            return Color.create_from_rgb(95, 158, 160, num_bits_per_pixel)
        elif color_constant == ColorConstant.GOLDENROD:
            return Color.create_from_rgb(218, 165, 32, num_bits_per_pixel)
        elif color_constant == ColorConstant.ORANGE:
            return Color.create_from_rgb(255, 165, 0, num_bits_per_pixel)
        elif color_constant == ColorConstant.GOLD:
            return Color.create_from_rgb(255, 215, 0, num_bits_per_pixel)
        elif color_constant == ColorConstant.FOREST_GREEN:
            return Color.create_from_rgb(34, 139, 34, num_bits_per_pixel)
        elif color_constant == ColorConstant.CORNFLOWER_BLUE:
            return Color.create_from_rgb(100, 149, 237, num_bits_per_pixel)
        elif color_constant == ColorConstant.NAVY:
            return Color.create_from_rgb(0, 0, 128, num_bits_per_pixel)
        elif color_constant == ColorConstant.TURQUOISE:
            return Color.create_from_rgb(64, 224, 208, num_bits_per_pixel)
        elif color_constant == ColorConstant.DARK_SLATE_BLUE:
            return Color.create_from_rgb(72, 61, 139, num_bits_per_pixel)
        elif color_constant == ColorConstant.LIGHT_BLUE:
            return Color.create_from_rgb(173, 216, 230, num_bits_per_pixel)
        elif color_constant == ColorConstant.INDIAN_RED:
            return Color.create_from_rgb(205, 92, 92, num_bits_per_pixel)
        elif color_constant == ColorConstant.VIOLET_RED:
            return Color.create_from_rgb(208, 32, 144, num_bits_per_pixel)
        elif color_constant == ColorConstant.LIGHT_STEEL_BLUE:
            return Color.create_from_rgb(176, 196, 222, num_bits_per_pixel)
        elif color_constant == ColorConstant.MEDIUM_BLUE:
            return Color.create_from_rgb(0, 0, 205, num_bits_per_pixel)
        elif color_constant == ColorConstant.KHAKI:
            return Color.create_from_rgb(240, 230, 140, num_bits_per_pixel)
        elif color_constant == ColorConstant.VIOLET:
            return Color.create_from_rgb(238, 130, 238, num_bits_per_pixel)
        elif color_constant == ColorConstant.FIREBRICK:
            return Color.create_from_rgb(178, 34, 34, num_bits_per_pixel)
        elif color_constant == ColorConstant.MIDNIGHT_BLUE:
            return Color.create_from_rgb(25, 25, 112, num_bits_per_pixel)
        else:
            raise NotSupportedException("Invalid color constant given.")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create a color, please refer to the class methods.

        :raises NotPossibleException: If the class cannot be initialized by default init.

        .. versionadded:: ids_peak_icv 1.0
        """
        try:
            self._color_code: int = kwargs["_color_code"]
        except KeyError:
            raise NotPossibleException(
                "Cannot initialize Color with arguments. Please use a class method.")

    @property
    def __red(self) -> int:
        """
        Get the red value.

        :return: The red value.

        .. versionadded:: ids_peak_icv 1.0
        """
        return (self._color_code >> 32) & 0xFFFF

    @property
    def __green(self) -> int:
        """
        Get the green value.

        :return: The green value.

        .. versionadded:: ids_peak_icv 1.0
        """
        return (self._color_code >> 16) & 0xFFFF

    @property
    def __blue(self) -> int:
        """
        Get the blue value.

        :return: The blue value.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._color_code & 0xFFFF

    @property
    def rgb(self) -> tuple[int, int, int]:
        """
        The color as a tuple of red, green and blue values.

        :return: Tuple with format (r, g, b)

        .. versionadded:: ids_peak_icv 1.0
        """
        return self.__red, self.__green, self.__blue

    @property
    def color_code(self) -> int:
        """
        Get the color code.

        :return: The color as an integer.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._color_code

    def __eq__(self, other: object) -> bool:
        """
        Check if two Color objects are equal.

        :param other: (Color): Another Color object.

        :return: True if equal, False otherwise.

        .. versionadded:: ids_peak_icv 1.0
        """

        if not isinstance(other, Color):
            return False

        return self._color_code == other._color_code

    def __ne__(self, other: object) -> bool:
        """
        Check if two Color objects are not equal.

        :param other: (Color): Another Color object.

        :return: True if not equal, False otherwise.

        .. versionadded:: ids_peak_icv 1.0
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        """
        :return: String representation of the object.

        .. versionadded:: ids_peak_icv 1.0
        """
        return f"Color(r: {self.__red}, g: {self.__green}, b: {self.__blue})"


class ColorPalette(Color):
    """
    Class holding a color palette (a set of colors).

    .. ingroup:: ids_peak_icv_python_painting

    .. versionadded:: ids_peak_icv 1.0
    """

    @classmethod
    def create_from_colors(cls, *args: Color) -> ColorPalette:
        """
        Create a pallet from a number of Colors.

        :param args: Comma separated Colors.
        :return: A ColorPalette object.

        .. versionadded:: ids_peak_icv 1.0
        """
        return ColorPalette(_color_palette=args)

    @classmethod
    def create_from_palette_constant(cls, color_palette_constant: ColorPaletteConstant,
                                     num_bits_per_pixel: int = 8) -> ColorPalette:
        """
        Create a pallet with a specific number of colors.

        The colors in the palett are

        - RED, GREEN, BLUE (for COLORED_3)
        - RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN (for COLORED_6)

        :param color_palette_constant: A ColorPaletteConstant.
        :param num_bits_per_pixel: Number of bits per pixel. Defaults to 8.
        :return: A ColorPalette object.

        .. versionadded:: ids_peak_icv 1.0
        """
        return ColorPalette(
            _color_palette=ColorPalette.__create_from_color_palette_constant(color_palette_constant,
                                                                             num_bits_per_pixel))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create a color palette, please refer to the class methods.

        :raises NotPossibleException: If the class cannot be initialized by default.

        .. versionadded:: ids_peak_icv 1.0
        """

        try:
            self._colorPalette = kwargs["_color_palette"]
        except KeyError:
            raise NotPossibleException(
                "Cannot initialize ColorPalette with arguments. Please use a class method.")

        self._colorPaletteIndex = 0
        Color.__init__(self, _color_code=self._colorPalette[self._colorPaletteIndex]._color_code)

    @property
    def rgb(self) -> tuple[int, int, int]:
        """
        Get the next color of the palette as a tuple with the red, green and blue values.

        :return: Tuple with format (r, g, b).

        .. versionadded:: ids_peak_icv 1.0
        """
        rgb_value = super().rgb
        self.__next_color()
        return rgb_value

    @property
    def color_code(self) -> int:
        """
        Get the next color of the palette as an integer.

        :return: The color as an integer.

        .. versionadded:: ids_peak_icv 1.0
        """
        color_code_value = super().color_code
        self.__next_color()
        return color_code_value

    def __next_color(self) -> None:
        self._colorPaletteIndex = (self._colorPaletteIndex + 1) % (len(self._colorPalette))
        self._color_code = self._colorPalette[self._colorPaletteIndex]._color_code

    @classmethod
    def __create_from_color_palette_constant(cls, color_palette_constant: ColorPaletteConstant,
                                             num_bits_per_pixel: int) -> list[Color]:
        if color_palette_constant == ColorPaletteConstant.COLORED_3:
            return [Color.create_from_constant(ColorConstant.RED, num_bits_per_pixel),
                    Color.create_from_constant(ColorConstant.GREEN, num_bits_per_pixel),
                    Color.create_from_constant(ColorConstant.BLUE, num_bits_per_pixel)]
        elif color_palette_constant == ColorPaletteConstant.COLORED_6:
            return [Color.create_from_constant(ColorConstant.RED, num_bits_per_pixel),
                    Color.create_from_constant(ColorConstant.GREEN, num_bits_per_pixel),
                    Color.create_from_constant(ColorConstant.BLUE, num_bits_per_pixel),
                    Color.create_from_constant(ColorConstant.YELLOW, num_bits_per_pixel),
                    Color.create_from_constant(ColorConstant.MAGENTA, num_bits_per_pixel),
                    Color.create_from_constant(ColorConstant.CYAN, num_bits_per_pixel)]
        return []
