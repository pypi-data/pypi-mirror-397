from __future__ import annotations

import numpy

from ids_peak_icv.pipeline._internal.color_matrix_transformation_module import ColorMatrixTransformationModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class ColorCorrectionFeature(IFeature):
    """
    Color correction applies a 3x3 color correction matrix to the image.

    @supportedPixelformats{ColorMatrixTransformation}

    Color correction is typically used to convert colors from a camera sensor’s native RGB space to a standard color space,
    or to perform color balancing and correction.

    When performing color correction, a 3x3 color correction matrix is applied to the color values of the image.

    The color correction matrix is represented as a 3×3 float array::

        +--------+--------+--------+
        | m_00   | m_01   | m_02   |
        +--------+--------+--------+
        | m_10   | m_11   | m_12   |
        +--------+--------+--------+
        | m_20   | m_21   | m_22   |
        +--------+--------+--------+

    Each element `m_ij` defines how much of the input channel `j` contributes to the output channel `i`.
    For example, `m_01` is the contribution of the green input to the red output.

    The matrix is applied as follows:
    ```python
        red_value_out   = m_00 * red_value_in + m_01 * green_value_in + m_02 * blue_value_in;
        green_value_out = m_10 * red_value_in + m_11 * green_value_in + m_12 * blue_value_in;
        blue_value_out  = m_20 * red_value_in + m_21 * green_value_in + m_22 * blue_value_in;
    ```

    where red_value_in, green_value_in, and blue_value_in are the input red, green, and blue channel values, respectively,
    and red_value_out, green_value_out, and blue_value_out are the corresponding corrected output values.
    All RGB values are normalized to the range [0.0, 1.0].

    .. warning:: Improper color correction matrices may result in color shifts, clipping, or unnatural colors.

    The default value for the color correction matrix is the identity matrix.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: ColorMatrixTransformationModule) -> None:
        """
        Creates a ColorCorrectionFeature for an existing color matrix transformation module.
        :param module: Reference to the underlying module

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module = module

    @property
    def enabled(self) -> bool:
        """
        Indicates whether the feature is currently enabled.
        :return: True if enabled; otherwise, False.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.color_correction_enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.color_correction_enabled = value

    def reset_to_default(self) -> None:
        """
        Resets the color correction matrix to identity matrix.
        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.reset_to_default()

    @property
    def matrix(self) -> numpy.ndarray:
        """
        Gets the current color correction matrix.
        :return: The color correction matrix currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.matrix

    @matrix.setter
    def matrix(self, matrix: numpy.ndarray) -> None:
        """
        Sets the color correction matrix.
        :param matrix: A floating-point matrix representing the color correction matrix.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.matrix = matrix
