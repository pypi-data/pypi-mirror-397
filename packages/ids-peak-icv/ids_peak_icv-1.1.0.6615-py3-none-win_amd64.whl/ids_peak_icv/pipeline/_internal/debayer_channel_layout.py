from __future__ import annotations

from enum import Enum

from ids_peak_icv.exceptions import NotSupportedException


class DebayerChannelLayout(Enum):
    """
    Specifies the channel layout used by the debayer module in image processing pipelines.

    .. ingroup:: ids_peak_icv_python_pipeline_modules
    .. versionadded:: ids_peak_icv 1.0
    """
    RGB = 0
    """
    Red-Green-Blue format with 3 channels.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    BGR = 1
    """
    Blue-Green-Red format with 3 channels.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    RGBA = 2
    """
    Red-Green-Blue-Alpha format with 4 channels.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    BGRA = 3
    """
    Blue-Green-Red-Alpha format with 4 channels.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    @property
    def string_value(self) -> str:
        """
        Return the string identifier for this channel layout.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self.name

    @staticmethod
    def create_from_string_value(string_value: str) -> DebayerChannelLayout:
        if string_value == "RGB":
            return DebayerChannelLayout.RGB
        if string_value == "BGR":
            return DebayerChannelLayout.BGR
        if string_value == "RGBA":
            return DebayerChannelLayout.RGBA
        if string_value == "BGRA":
            return DebayerChannelLayout.BGRA

        raise NotSupportedException(f"The given channel layout is not supported. Given: {string_value}")
