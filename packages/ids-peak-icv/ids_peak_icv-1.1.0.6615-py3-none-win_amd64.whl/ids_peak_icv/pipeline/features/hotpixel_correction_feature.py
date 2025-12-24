from __future__ import annotations

import numpy as np

from ids_peak_icv import Image
from ids_peak_icv.pipeline._internal.hotpixel_correction_module import HotpixelCorrectionModule
from ids_peak_icv.pipeline.features.ifeature import IFeature


class HotpixelCorrectionFeature(IFeature):
    """
    HotpixelCorrection detects and corrects hot pixels in camera images.

    @supportedPixelformats{HotpixelCorrection}

    The HotpixelCorrection class is responsible for identifying and correcting defective pixels that consistently
    report higher-than-expected intensity values.

    It allows fine-tuning of the detection sensitivity and management of a hot pixel
    correction list, which is applied during image processing through the process() method.

    The default value is an empty hotpixel correction list.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_features
    """

    def __init__(self, module: HotpixelCorrectionModule) -> None:
        """
        Creates a HotpixelCorrectionFeature for an existing hotpixel correction module.
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
        return self._module.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enables or disables the feature.
        :param value: Set to True to enable the feature, or False to disable it.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.enabled = value

    def reset_to_default(self) -> None:
        """
        Resets the pixel list (empty list).

        .. note:: The enabled state does not change when calling this function.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.reset_to_default()

    @property
    def hotpixel_list(self) -> np.ndarray:
        """
        Gets the current pixel list.
        :return: The pixel list currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._module.hotpixel_list

    @hotpixel_list.setter
    def hotpixel_list(self, pixel_list: np.ndarray) -> None:
        """
        Sets the pixel list.
        :param pixel_list: A list of points representing the hotpixel.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.hotpixel_list = pixel_list

    def detect(self, image: Image, sensitivity: int = 3, gain_factor: float = 1.0) -> None:
        """
        Performs immediate hot pixel detection on the given image.

        This method analyzes the provided image and detects hot pixels based on the
        sensitivity setting. The results are stored internally and can be accessed using pixel_list.

        Note: Calling this function will overwrite any existing hot pixel list previously set via pixel_list.

        :param image:       The input image to analyze for hot pixel detection.
        :param sensitivity: Sensitivity for hot pixel detection. A higher sensitivity
                            may result in detecting more hot pixels, including possible
                            false positives.
        :param gain_factor: Gain factor applied to the image. Used to account for
                            increased noise levels when detecting hot pixels.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._module.detect(image, sensitivity, gain_factor)
