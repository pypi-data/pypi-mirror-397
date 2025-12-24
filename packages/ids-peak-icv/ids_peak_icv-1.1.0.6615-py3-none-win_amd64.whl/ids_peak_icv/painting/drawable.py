import abc

from ids_peak_icv.painting.drawing_options import DrawingOptions
from ids_peak_icv.datatypes.image import Image


class IDrawable:
    """
    Interface for drawable objects.

    .. versionadded:: ids_peak_icv 1.1
    """

    @abc.abstractmethod
    def _draw(self, image: Image, drawing_options: DrawingOptions) -> None:
        pass
