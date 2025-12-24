import ctypes
from typing import cast

import numpy as np

from ids_peak_common import Interval, PixelFormat
from ids_peak_common.serialization import IArchive
from ids_peak_common.pipeline.modules.iautofeature_module import IAutoFeature
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import (peak_icv_color_correction_matrix,
                                              peak_icv_color_matrix_transformation_handle, peak_icv_interval_f)
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.pipeline._internal.module_base import ModuleBase


class ColorMatrixTransformationModule(ModuleBase):
    """
    Color matrix transformation is an image pipeline module that applies a color correction matrix to an image.

    Provides the features ColorCorrectionFeature and SaturationFeature.

    Default configuration:
        - Color correction matrix = 3x3 identity matrix
        - Saturation = 1.0

    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_MATRIX: np.ndarray = np.eye(3)
    """
    Default color correction matrix value.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_SATURATION: float = 1.0
    """
    Default saturation value.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    SUPPORTED_PIXEL_FORMATS = [
        PixelFormat.RGB_8, PixelFormat.RGB_10, PixelFormat.RGB_12, PixelFormat.BGR_8, PixelFormat.BGR_10,
        PixelFormat.BGR_12, PixelFormat.RGBA_8, PixelFormat.RGBA_10, PixelFormat.RGBA_12, PixelFormat.BGRA_8,
        PixelFormat.BGRA_10, PixelFormat.BGRA_12
    ]

    def __init__(self) -> None:
        """
        Initialize a color matrix transformation module with default settings.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        self._color_correction_enabled = True
        self._saturation_enabled = True
        self._matrix: None | np.ndarray = None
        self._saturation: float | None = None
        self._auto_feature_module: IAutoFeature | None = None

        self.reset_to_default()

        _color_matrix_transformation_handle = peak_icv_color_matrix_transformation_handle()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ColorMatrixTransformation_Create,
            ctypes.pointer(_color_matrix_transformation_handle)
        )
        self._handle = _color_matrix_transformation_handle

    def __del__(self) -> None:
        if hasattr(self, "_handle") and self._handle:
            lib_loader.dll().peak_icv_Preprocessing_ColorMatrixTransformation_Destroy(self._handle)

    @property
    def type(self) -> str:
        """
        Returns the type of the module for serialization purposes.

        :return: Module type.

        .. versionadded:: ids_peak_icv 1.0
        """
        return "ColorMatrixTransformation"

    @property
    def enabled(self) -> bool:
        """
        Get whether this module is enabled.

        When disabled, :func:`process` returns the input image unchanged.

        :return: True if the module is enabled, False otherwise.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self.color_correction_enabled or self.saturation_enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """
        Enable or disable the module.

        When disabled, :func:`process` returns the input image unchanged.

        :param enabled: True to enable, False to disable.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._color_correction_enabled = enabled
        self._saturation_enabled = enabled
        self._update_ccm_in_auto_feature_module()

    @property
    def matrix(self) -> np.ndarray:
        """
        Gets the current color correction matrix.

        :return: The color correction matrix currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return cast(np.ndarray, self._matrix)

    @matrix.setter
    def matrix(self, matrix: np.ndarray) -> None:
        """
        Sets the current color correction matrix.

        :param matrix: The color correction matrix.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._matrix = matrix
        self._apply_matrix()
        self._update_ccm_in_auto_feature_module()

    @property
    def saturation(self) -> float:
        """
        Gets the current saturation value.

        :return: The saturation value currently set.

        .. versionadded:: ids_peak_icv 1.0
        """
        return cast(float, self._saturation)

    @saturation.setter
    def saturation(self, saturation: float) -> None:
        """
        Sets the current saturation value.

        :param saturation: The saturation value.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._saturation = saturation
        self._apply_saturation()
        self._update_ccm_in_auto_feature_module()

    @property
    def saturation_range(self) -> Interval:
        """
        Gets the valid range for saturation.

        :return: The valid saturation range.

        .. versionadded:: ids_peak_icv 1.0
        """
        c_interval = peak_icv_interval_f()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ColorMatrixTransformation_GetSaturationRange,
            self._handle, ctypes.pointer(c_interval))
        return Interval(c_interval.minimum, c_interval.maximum)

    @property
    def color_correction_enabled(self) -> bool:
        """
        Whether color correction is enabled.

        :return: True if color correction is applied during processing.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._color_correction_enabled

    @color_correction_enabled.setter
    def color_correction_enabled(self, enabled: bool) -> None:
        """
        Whether color correction is enabled.

        :param enabled: True if color correction is enabled.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._color_correction_enabled = enabled
        self._apply_matrix()
        self._update_ccm_in_auto_feature_module()

    @property
    def saturation_enabled(self) -> bool:
        """
        Whether saturation is enabled.

        :return: True if saturation is applied during processing.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._saturation_enabled

    @saturation_enabled.setter
    def saturation_enabled(self, enabled: bool) -> None:
        """
        Whether saturation is enabled.

        :param enabled: True if saturation is enabled.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._saturation_enabled = enabled
        self._apply_saturation()

    def process(self, input_image: Image) -> Image:
        """
        Processes the input image and returns a color corrected and/or saturated output image.

        @supportedPixelformats{ColorMatrixTransformation}

        Images with other formats are passed through unmodified.

        This operation disregards any specified image regions and processes the entire image.

        :param input_image: The input image to be processed.

        :return: A new image with color correction and/or saturation applied.

        .. versionadded:: ids_peak_icv 1.0
        """
        if not self.enabled:
            return input_image

        if input_image.pixel_format not in self.SUPPORTED_PIXEL_FORMATS:
            return input_image

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ColorMatrixTransformation_ProcessInplace,
            self._handle,
            input_image._handle
        )
        return input_image

    def reset_to_default(self) -> None:
        """
        Resets all module settings.

        Restores the module configuration to its default values:
        - matrix = identity
        - saturation = 1.0

        .. versionadded:: ids_peak_icv 1.0
        """
        self._matrix = self.DEFAULT_MATRIX
        self._saturation = self.DEFAULT_SATURATION

    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the object's internal state into the provided archive.

        This function populates the given archive with all parameters required to fully represent the current state of the object.
        It ensures that the object can be reconstructed or transmitted accurately by saving all relevant data members
        in a consistent and structured format.

        :return: The serialized module's internal state.

        .. versionadded:: ids_peak_icv 1.0
        """
        super().serialize(archive)

        saturation_archive = archive.create_archive()
        saturation_archive.set("Enabled", self._saturation_enabled)
        saturation_archive.set("Value", cast(float, self._saturation))
        archive.set("Saturation", saturation_archive)

        color_correction_matrix_archive = archive.create_archive()
        color_correction_matrix_archive.set("Enabled", self._color_correction_enabled)
        color_correction_matrix_archive.set("Matrix", cast(list[float], cast(np.ndarray, self._matrix).flatten().tolist()))
        archive.set("ColorCorrection", color_correction_matrix_archive)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores the object's state from the provided archive.

        This function reads and applies all necessary parameters from the given archive
        to reconstruct the internal state of the object.
        It ensures that the object is restored to a valid and consistent state.

        :param archive: The source archive containing the serialized parameters.

        :raises CorruptedException: If Archive is malformed, misses keys or the values are invalid
        :raises NotSupportedException: If the 'Version' entry indicates an unsupported version.

        .. note:: This function requires that the archive contains all expected fields as produced by
              a corresponding serialize() call.

        .. versionadded:: ids_peak_icv 1.0
        """
        super()._validate_version(archive)

        saturation_archive = archive.get_archive("Saturation")
        self._saturation_enabled = saturation_archive.get("Enabled", bool)
        self._saturation = saturation_archive.get("Value", float)

        color_correction_matrix_archive = archive.get_archive("ColorCorrection")
        self._color_correction_enabled = color_correction_matrix_archive.get("Enabled", bool)
        self._matrix = np.array(color_correction_matrix_archive.get("Matrix", list)).reshape(3, 3)

    def _set_autofeature_module(self, auto_feature_module: IAutoFeature | None) -> None:
        self._auto_feature_module = auto_feature_module
        self._update_ccm_in_auto_feature_module()

    def _apply_matrix(self) -> None:
        matrix = self._matrix if self._color_correction_enabled else self.DEFAULT_MATRIX

        c_matrix = peak_icv_color_correction_matrix.from_buffer_copy(
            np.asarray(matrix, dtype=np.float32).flatten().tobytes())

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ColorMatrixTransformation_SetColorCorrectionMatrix,
            self._handle,
            c_matrix
        )

    def _apply_saturation(self) -> None:
        saturation = cast(float, self._saturation) if self._saturation_enabled else self.DEFAULT_SATURATION
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ColorMatrixTransformation_SetSaturation,
            self._handle,
            ctypes.c_float(saturation)
        )

    def _effective_matrix(self) -> np.ndarray:
        c_matrix = peak_icv_color_correction_matrix()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_ColorMatrixTransformation_GetEffectiveMatrix,
            self._handle, ctypes.byref(c_matrix)
        )
        return cast(np.ndarray, np.frombuffer(memoryview(c_matrix), dtype=np.float32).reshape(3, 3).copy())

    def _update_ccm_in_auto_feature_module(self) -> None:
        if self._auto_feature_module:
            matrix = (self._effective_matrix() if (self._saturation_enabled
                                                   or self._color_correction_enabled) else np.identity(3, dtype=float))
            self._auto_feature_module.set_color_correction_matrix(matrix.flatten().tolist())

