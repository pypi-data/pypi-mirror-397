from ids_peak_icv.painting.color import Color, ColorConstant
from ids_peak_icv.painting.opacity import Opacity


class DrawingOptions:
    """
    Drawing options.

    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self) -> None:
        self.color = Color.create_from_constant(ColorConstant.RED, 8)
        self.opacity = Opacity(100)
