from __future__ import annotations

import ctypes
from typing import TypeAlias, cast

import numpy as np
import numpy.typing as npt

from ids_peak_common import Interval, Point
from ids_peak_common.exceptions import NotSupportedException
from ids_peak_common.serialization import IArchive
from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import (peak_icv_hotpixel_correction_handle, peak_common_interval_u,
                                              peak_icv_point)
from ids_peak_icv.backend.utils import execute_and_map_return_codes, create_array
from ids_peak_icv.datatypes.image import Image
from ids_peak_icv.pipeline._internal import ModuleBase

# Note: We loose type info here, as it is stored as a pointer to a python object
PointArray: TypeAlias = npt.NDArray[np.object_]


class HotpixelCorrectionModule(ModuleBase):
    """
    Hotpixel correction is an image pipeline module for detecting and correcting hot pixels in camera images.

    Provides the feature HotpixelCorrectionFeature.

    .. versionadded:: ids_peak_icv 1.0
    """

    DEFAULT_HOTPIXEL_LIST: np.ndarray = np.empty(0, dtype=Point)
    """
    Default hotpixel list (empty list).
    
    .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self) -> None:
        """
        Creates a HotpixelCorrectionModule module with default settings (no correction).

        .. versionadded:: ids_peak_icv 1.0
        """
        super().__init__()

        self._hotpixel_correction_enabled = True
        self._hotpixel_list: np.ndarray | None = self.DEFAULT_HOTPIXEL_LIST

        _hotpixel_correction_handle = peak_icv_hotpixel_correction_handle()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_HotpixelCorrection_Create,
            ctypes.pointer(_hotpixel_correction_handle)
        )
        self._handle = _hotpixel_correction_handle

    @property
    def type(self) -> str:
        """
        Returns the type of the module for serialization purposes.

        :return: Module type.

        .. versionadded:: ids_peak_icv 1.0
        """
        return "HotpixelCorrection"

    @property
    def enabled(self) -> bool:
        """
        Gets whether this module is enabled.

        When disabled, :func:`process` returns the input image unchanged.

        :return: True if the module is enabled, False otherwise.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._hotpixel_correction_enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """
        Enable or disable the module.

        When disabled, :func:`process` returns the input image unchanged.

        :param enabled: True to enable, False to disable.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._hotpixel_correction_enabled = enabled
        self._apply_pixel_list()

    @property
    def hotpixel_list(self) -> PointArray:
        """
        Gets the current array of known hot pixels.

        :return: An array containing the positions of all configured hot pixels.

        .. versionadded:: ids_peak_icv 1.0
        """
        if self._hotpixel_list is not None:
            return self._hotpixel_list

        self._call_backend_get_list()

        return cast(np.ndarray, self._hotpixel_list)

    @hotpixel_list.setter
    def hotpixel_list(self, pixel_list: PointArray) -> None:
        """
        Sets the array of known hot pixels.

        :param pixel_list: An array of hot pixel positions to use.

        .. versionadded:: ids_peak_icv 1.0
        """
        if not isinstance(pixel_list, np.ndarray):
            raise NotSupportedException(
                "Parameter points has to be a numpy array of Point objects.")

        if pixel_list.size == 0:
            self.reset_to_default()
        self._hotpixel_list = pixel_list
        self._apply_pixel_list()

    @property
    def sensitivity_range(self) -> Interval:
        """
        Gets the valid range for sensitivity.

        :return: The valid sensitivity range.

        .. versionadded:: ids_peak_icv 1.0
        """
        c_interval = peak_common_interval_u()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_HotpixelCorrection_GetSensitivityRange,
            self._handle, ctypes.pointer(c_interval))
        return Interval(c_interval.minimum, c_interval.maximum)

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

        :raises NotSupportedException: If image has any other than the supported pixel formats.

        .. versionadded:: ids_peak_icv 1.0
        """
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_HotpixelCorrection_Detect,
            self._handle, image._handle, ctypes.c_size_t(sensitivity), ctypes.c_float(gain_factor))
        self._call_backend_get_list()

    def process(self, input_image: Image) -> Image:
        """
        Applies hot pixel correction to the input image in place and returns a reference to the modified image.

        @supportedPixelformats{HotpixelCorrection}

        The correction is performed based on the current configuration of the module. The operation modifies the
        input image directly and does not create a copy.

        @supportedPixelformats{HotpixelCorrection}

        Images with other formats are passed through unmodified.

        This operation disregards any specified image regions and processes the entire image.

        :param input_image: The input image to be processed and corrected.

        :raises NotSupportedException: If image has any other than the supported pixel formats.

        :return: A new image with hotpixel correction applied.

        .. versionadded:: ids_peak_icv 1.0
        """
        if not self.enabled:
            return input_image

        if self.hotpixel_list.size == 0:
            return input_image

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_HotpixelCorrection_ProcessInplace,
            self._handle, input_image._handle)

        return input_image

    def reset_to_default(self) -> None:
        """
        Resets all module settings.

        Restores the module configuration to its default values:
        - hotpixel_list = empty np.ndarray of type Point

        .. versionadded:: ids_peak_icv 1.0
        """
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_HotpixelCorrection_ResetList,
            self._handle)
        self._hotpixel_list = self.DEFAULT_HOTPIXEL_LIST

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

        archive.set("Enabled", self._enabled)

        pixel_list_archives = []
        for pixel in self.hotpixel_list:
            pixel_archive = archive.create_archive()
            pixel_archive.set("X", pixel.x)
            pixel_archive.set("Y", pixel.y)
            pixel_list_archives.append(pixel_archive)
        archive.set("HotpixelList", pixel_list_archives)

    def deserialize(self, archive: IArchive) -> None:
        """
        Restores the object's state from the provided archive.

        This function reads and applies all necessary parameters from the given archive to reconstruct the internal state of the object.
        It ensures that the object is restored to a valid and consistent state.

        :param archive: The source archive containing the serialized parameters.

        :raises CorruptedException: If Archive is malformed, misses keys or the values are invalid
        :raises NotSupportedException: If the 'Version' entry indicates an unsupported version.

        .. note:: This function requires that the archive contains all expected fields as produced by a corresponding serialize() call.

        .. versionadded:: ids_peak_icv 1.0
        """

        super().deserialize(archive)

        pixel_archives = archive.get("HotpixelList", list)
        pixel_list = []
        for pixel_archive in pixel_archives:
            pixel_x = pixel_archive.get("X", int)
            pixel_y = pixel_archive.get("Y", int)
            pixel_list.append(Point(pixel_x, pixel_y))

        self._hotpixel_list = np.array(pixel_list)

    def _apply_pixel_list(self) -> None:
        pixel_list = cast(np.ndarray, self._hotpixel_list) if self._enabled else self.DEFAULT_HOTPIXEL_LIST

        if pixel_list.size == 0:
            self.reset_to_default()  # reset_to_default set the internal hotpixel list to an empty list!
            return

        self._call_backend_set_list(pixel_list)

    def _call_backend_set_list(self, pixel_list: npt.NDArray) -> None:
        size = len(pixel_list)
        c_points = create_array(peak_icv_point, size)

        for i, pixel in enumerate(pixel_list):
            c_points[i] = peak_icv_point(pixel.x, pixel.y)

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_HotpixelCorrection_SetList,
            self._handle, c_points, size
        )

    def _call_backend_get_list(self) -> None:
        c_count = ctypes.c_size_t()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_Preprocessing_HotpixelCorrection_GetList_GetCount,
            self._handle, ctypes.pointer(c_count)
        )

        if c_count.value == 0:
            self._hotpixel_list = None
            return

        c_points = create_array(peak_icv_point, c_count.value)
        execute_and_map_return_codes(lib_loader.dll().peak_icv_Preprocessing_HotpixelCorrection_GetList,
                                     self._handle, c_points, c_count)

        self._hotpixel_list = np.array([Point(p.x, p.y) for p in c_points], dtype=object)
