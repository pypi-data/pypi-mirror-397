from __future__ import annotations
from enum import Enum

from ids_peak_icv.exceptions import NotSupportedException


class DebayerConversionPolicy(Enum):
    """
    Specifies the conditions under which the debayer module applies color conversion.

    .. ingroup:: ids_peak_icv_python_pipeline_modules
    .. versionadded:: ids_peak_icv 1.0
    """
    BYPASS = 0
    """
    Do not convert images.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    BAYER_ONLY = 1
    """
    Convert only Bayer-pattern images.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    BAYER_AND_MONO = 2
    """
    Convert both Bayer-pattern and monochrome images.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    @property
    def string_value(self) -> str:
        """
        Return the string identifier for this conversion policy.
        .. versionadded:: ids_peak_icv 1.0
        """
        mapping = {
            DebayerConversionPolicy.BYPASS: "Bypass",
            DebayerConversionPolicy.BAYER_ONLY: "BayerOnly",
            DebayerConversionPolicy.BAYER_AND_MONO: "BayerAndMono",
        }
        return mapping[self]

    @staticmethod
    def create_from_string_value(string_value: str) -> DebayerConversionPolicy:
        if string_value == "Bypass":
            return DebayerConversionPolicy.BYPASS
        if string_value == "BayerOnly":
            return DebayerConversionPolicy.BAYER_ONLY
        if string_value == "BayerAndMono":
            return DebayerConversionPolicy.BAYER_AND_MONO

        raise NotSupportedException(
            f"The given conversion conversion policy is not supported. Given: {string_value}")
