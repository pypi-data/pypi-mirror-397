from __future__ import annotations

import ctypes
from typing import Any, cast

import numpy as np

from ids_peak_icv import lib_loader
from ids_peak_icv.backend.datatypes import peak_icv_calibration_parameters
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.exceptions import NotPossibleException, CorruptedException, MismatchException
from ids_peak_icv.calibration.intrinsic_parameters import IntrinsicParameters
from ids_peak_icv.calibration.extrinsic_parameters import ExtrinsicParameters


class CalibrationParameters:
    """
    Represents the calibration parameters, which include intrinsic and extrinsic
    parameters.

    .. ingroup:: ids_peak_icv_python_calibration
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        In order to create CalibrationParameters, please refer to the classmethods.

        .. versionadded:: ids_peak_icv 1.1
        """
        try:
            if "_parameters" in kwargs:
                parameters = kwargs["_parameters"]
                self._intrinsic_parameters = IntrinsicParameters(_parameters=parameters.intrinsic_parameters)
                self._extrinsic_parameters = ExtrinsicParameters(_parameters=parameters.extrinsic_parameters)
            elif "_extrinsic_parameters" in kwargs and "_intrinsic_parameters" in kwargs:
                self._intrinsic_parameters = kwargs["_intrinsic_parameters"]
                self._extrinsic_parameters = kwargs["_extrinsic_parameters"]
            else:
                raise KeyError
        except KeyError:
            raise NotPossibleException(
                f"{self.__class__.__name__} shall not be initialized directly. Use class methods."
            )

    @classmethod
    def create_from_file(cls, file_path: str) -> CalibrationParameters:
        """
        Creates an instance of CalibrationParameters from a file.

        :param file_path: An existing file path to a JSON file containing the calibration parameters.

        :raises IOException: If the given file_path does not exist, or the permissions are not sufficient
        to read it.
        :raises CorruptedException: If the file content is corrupted.

        :return: A new instance of CalibrationParameters

        .. versionadded:: ids_peak_icv 1.1
        """
        c_file_path = file_path.encode('utf-8')
        parameters = peak_icv_calibration_parameters()

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_CalibrationParameters_CreateFromFile,
            ctypes.pointer(parameters), ctypes.sizeof(parameters),
            ctypes.c_char_p(c_file_path)
        )

        return CalibrationParameters(_parameters=parameters)

    @classmethod
    def create_from_parameters(cls, intrinsic_parameters: IntrinsicParameters,
                               extrinsic_parameters: ExtrinsicParameters) -> CalibrationParameters:
        """
        Creates an instance of CalibrationParameters using intrinsic and extrinsic parameters.

        :param intrinsic_parameters: The intrinsic camera parameters.
        :param extrinsic_parameters: The extrinsic camera parameters.

        :return: A new instance of CalibrationParameters

        .. versionadded:: ids_peak_icv 1.1
        """
        return CalibrationParameters(
            _intrinsic_parameters=intrinsic_parameters,
            _extrinsic_parameters=extrinsic_parameters
        )

    @classmethod
    def create_from_binary(cls, binary: np.ndarray) -> CalibrationParameters:
        """
        Creates an instance of CalibrationParameters from binary data.

        :param binary: A NumPy array containing the binary representation of calibration parameters.

        :return: A new instance of CalibrationParameters

        :raises CorruptedException: If the binary calibration parameters are corrupted.

        .. versionadded:: ids_peak_icv 1.1
        """
        if binary.dtype != np.uint8:
            # todo test this
            raise MismatchException("Data type of the numpy array must be uint8")

        is_valid = ctypes.c_bool(False)
        size = len(binary)

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_ValidateBinary,
            binary.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)), size,
            ctypes.pointer(is_valid)
        )

        if not is_valid.value:
            raise CorruptedException("The given binary data is invalid")

        calibration_parameters = peak_icv_calibration_parameters()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_CalibrationParameters_CreateFromBinary,
            binary.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)), size,
            ctypes.pointer(calibration_parameters), ctypes.sizeof(calibration_parameters)
        )

        return CalibrationParameters(_parameters=calibration_parameters)

    def to_binary(self) -> np.ndarray:
        """
        Converts the CalibrationParameters instance to a binary representation.

        :return: A NumPy array containing the binary data.

        .. versionadded:: ids_peak_icv 1.1
        """

        calibration_parameters = peak_icv_calibration_parameters(
            intrinsic_parameters=self._intrinsic_parameters._parameters,
            extrinsic_parameters=self._extrinsic_parameters._parameters
        )

        binary_size = ctypes.c_size_t()
        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_CalibrationParameters_ToBinaryGetSizeInBytes,
            ctypes.sizeof(calibration_parameters), ctypes.pointer(binary_size)
        )
        data = np.zeros(binary_size.value, dtype=np.uint8)

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_CalibrationParameters_ToBinary,
            calibration_parameters, ctypes.sizeof(calibration_parameters),
            data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)), binary_size
        )

        return data

    @property
    def intrinsic_parameters(self) -> IntrinsicParameters:
        """
        Retrieves the intrinsic parameters of the calibration.

        :return: The intrinsic camera parameters.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._intrinsic_parameters

    @property
    def extrinsic_parameters(self) -> ExtrinsicParameters:
        """
        Retrieves the extrinsic parameters of the calibration.

        :return: The extrinsic camera parameters.

        .. versionadded:: ids_peak_icv 1.1
        """
        return self._extrinsic_parameters

    def save(self, file_path: str) -> None:
        """
        Saves the calibration parameters to a file.

        :param file_path: The path where the parameters should be saved.

        :raises IOException: If the file cannot be saved or permissions are insufficient.

        .. versionadded:: ids_peak_icv 1.1
        """
        c_file_path = file_path.encode('utf-8')

        parameters = peak_icv_calibration_parameters(
            intrinsic_parameters=self._intrinsic_parameters._parameters,
            extrinsic_parameters=self._extrinsic_parameters._parameters
        )

        execute_and_map_return_codes(
            lib_loader.dll().peak_icv_CalibrationParameters_SaveToFile,
            parameters, ctypes.sizeof(parameters),
            ctypes.c_char_p(c_file_path)
        )

    def __eq__(self, other: object) -> bool:
        """
        Compares two CalibrationParameters instances for equality.

        :param other: Another instance to compare.

        :return: True if both instances are equal, False otherwise.

        .. versionadded:: ids_peak_icv 1.1
        """

        if not isinstance(other, CalibrationParameters):
            return False

        return (self.intrinsic_parameters == other.intrinsic_parameters and
                self.extrinsic_parameters == other.extrinsic_parameters)
