from __future__ import annotations

import ctypes
from enum import Enum


class peak_icv_status(Enum):
    PEAK_ICV_STATUS_SUCCESS = 0
    PEAK_ICV_STATUS_LIBRARY_NOT_INITIALIZED = 1
    PEAK_ICV_STATUS_DYNAMIC_DEPENDENCY_MISSING = 2
    PEAK_ICV_STATUS_MISMATCH = 3
    PEAK_ICV_STATUS_NOT_SUPPORTED = 4
    PEAK_ICV_STATUS_NOT_POSSIBLE = 5
    PEAK_ICV_STATUS_NULL_POINTER = 6
    PEAK_ICV_STATUS_INVALID_HANDLE = 7
    PEAK_ICV_STATUS_OUT_OF_RANGE = 8
    PEAK_ICV_STATUS_MATH_ERROR = 9
    PEAK_ICV_STATUS_TARGET_NOT_FOUND = 10
    PEAK_ICV_STATUS_CORRUPTED = 11
    PEAK_ICV_STATUS_IO_ERROR = 12
    PEAK_ICV_STATUS_INTERNAL_ERROR = 13
    PEAK_ICV_STATUS_INVALID_BUFFER_SIZE = 14


class peak_icv_point_type(Enum):
    PEAK_ICV_POINT_TYPE_XYZ = 0,
    PEAK_ICV_POINT_TYPE_XYZ_I8 = 1,
    PEAK_ICV_POINT_TYPE_XYZ_I10 = 2,
    PEAK_ICV_POINT_TYPE_XYZ_I12 = 3,
    PEAK_ICV_POINT_TYPE_XY = 4


class peak_icv_interval(ctypes.Structure):
    _fields_ = [("minimum", ctypes.c_int32),
                ("maximum", ctypes.c_int32)]


class peak_common_interval_u(ctypes.Structure):
    _fields_ = [("minimum", ctypes.c_uint32),
                ("maximum", ctypes.c_uint32)]


class peak_icv_interval_f(ctypes.Structure):
    _fields_ = [("minimum", ctypes.c_float),
                ("maximum", ctypes.c_float)]


class peak_common_size(ctypes.Structure):
    _fields_ = [("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32)]


class peak_common_size_f(ctypes.Structure):
    _fields_ = [("width", ctypes.c_float),
                ("height", ctypes.c_float)]


class peak_icv_drawing_options(ctypes.Structure):
    _fields_ = [("color", ctypes.c_uint64),
                ("opacity", ctypes.c_uint32),
                ("line_width", ctypes.c_size_t)]


class peak_icv_point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int32),
                ("y", ctypes.c_int32)]


class peak_icv_point_u(ctypes.Structure):
    _fields_ = [("x", ctypes.c_uint32),
                ("y", ctypes.c_uint32)]


class peak_icv_point_f(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float)]


class peak_icv_point_xyz(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float),
                ("_", ctypes.c_float)]


class peak_icv_point_xyzi(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("z", ctypes.c_float),
                ("i", ctypes.c_uint16)]


class peak_common_rectangle(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int32),
                ("y", ctypes.c_int32),
                ("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32)]


class peak_common_rectangle_u(ctypes.Structure):
    _fields_ = [("x", ctypes.c_uint32),
                ("y", ctypes.c_uint32),
                ("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32)]


class peak_common_rectangle_f(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("width", ctypes.c_float),
                ("height", ctypes.c_float)]


class peak_common_version(ctypes.Structure):
    _fields_ = [("major", ctypes.c_uint32),
                ("minor", ctypes.c_uint32),
                ("patch", ctypes.c_uint32),
                ("revision", ctypes.c_uint32)]


class peak_icv_prism_distortion(ctypes.Structure):
    _fields_ = [("coefficients", ctypes.c_double * 4)]


class peak_icv_radial_distortion(ctypes.Structure):
    _fields_ = [("coefficients", ctypes.c_double * 6)]


class peak_icv_tangential_distortion(ctypes.Structure):
    _fields_ = [("coefficients", ctypes.c_double * 2)]


class peak_icv_tilt_distortion(ctypes.Structure):
    _fields_ = [("coefficients", ctypes.c_double * 2)]


class peak_icv_distortion_coefficients(ctypes.Structure):
    _fields_ = [("radial_distortion", peak_icv_radial_distortion),
                ("tangential_distortion", peak_icv_tangential_distortion),
                ("prism_distortion", peak_icv_prism_distortion),
                ("tilt_distortion", peak_icv_tilt_distortion)]


class peak_icv_coordinate_system(ctypes.Structure):
    _fields_ = [("origin", peak_icv_point_f),
                ("x_axis", peak_icv_point_f),
                ("y_axis", peak_icv_point_f),
                ("z_axis", peak_icv_point_f)]


class peak_icv_header(ctypes.Structure):
    _fields_ = [("marker", ctypes.c_uint32),
                ("type", ctypes.c_uint32),
                ("flags", ctypes.c_uint32),
                ("version", peak_common_version),
                ("crc", ctypes.c_uint32)]


peak_icv_binning = peak_icv_point_u


class peak_icv_intrinsic_parameters(ctypes.Structure):
    _fields_ = [
        ("image_size", peak_common_size),
        ("binning_factor", peak_icv_binning),
        ("distortion_coefficients", peak_icv_distortion_coefficients),
        ("focal_length_pixel_size_ratio", peak_icv_point_f),
        ("principle_point", peak_icv_point_f)]


class peak_icv_extrinsic_parameters(ctypes.Structure):
    _fields_ = [("rotation", peak_icv_point_xyz),
                ("translation", peak_icv_point_xyz)]


class peak_icv_calibration_parameters(ctypes.Structure):
    _fields_ = [("intrinsic_parameters", peak_icv_intrinsic_parameters),
                ("extrinsic_parameters", peak_icv_extrinsic_parameters)]


class peak_icv_image_info(ctypes.Structure):
    _fields_ = [
        ("pixel_format", ctypes.c_int),
        ("size", peak_common_size),
        ("buffer_size", ctypes.c_size_t),
        ("buffer", ctypes.POINTER(ctypes.c_uint8))]


class peak_icv_direction_vector(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double),
                ("y", ctypes.c_double)]


class peak_icv_reprojection_error(ctypes.Structure):
    _fields_ = [
        ("position", peak_icv_point_f),
        ("direction", peak_icv_point_f),
        ("length", ctypes.c_double),
        ("reserved", ctypes.c_uint8 * 40)]


peak_icv_binning_factor = peak_icv_point_u
peak_icv_downsampling_factor = peak_icv_point_u


class peak_icv_capture_information(ctypes.Structure):
    _fields_ = [
        ("binning_factor", peak_icv_binning_factor),
        ("relative_timestamp", ctypes.c_uint64),
        ("region_of_interest", peak_common_rectangle_u),
        ("reserved", ctypes.c_uint8 * 104)
    ]


class peak_icv_color_correction_matrix(ctypes.Structure):
    _fields_ = [
        ("data_1d", ctypes.c_float * 9)
    ]


class peak_icv_preprocessing_transformation_parameters(ctypes.Structure):
    _fields_ = [
        ("mirror_left_right", ctypes.c_bool),
        ("mirror_up_down", ctypes.c_bool),
        ("rotation_angle", ctypes.c_uint32)
    ]


class peak_icv_region_handle(ctypes.c_void_p):
    pass


class peak_icv_polygon_handle(ctypes.c_void_p):
    pass


class peak_icv_calibration_result_handle(ctypes.c_void_p):
    pass


class peak_icv_calibration_view_handle(ctypes.c_void_p):
    pass


class peak_icv_calibration_plate_handle(ctypes.c_void_p):
    pass


class peak_icv_point_cloud_handle(ctypes.c_void_p):
    pass


class peak_icv_image_handle(ctypes.c_void_p):
    pass


class peak_icv_undistortion_handle(ctypes.c_void_p):
    pass


class peak_icv_image_converter_handle(ctypes.c_void_p):
    pass


class peak_icv_color_matrix_transformation_handle(ctypes.c_void_p):
    pass


class peak_icv_tone_curve_correction_handle(ctypes.c_void_p):
    pass


class peak_icv_downsampling_handle(ctypes.c_void_p):
    pass


class peak_icv_hotpixel_correction_handle(ctypes.c_void_p):
    pass


def ctypes_objects_equal(obj1: object, obj2: object) -> bool:
    """
    Compares two ctypes objects for equality by recursively comparing their fields.

    Args:
        obj1: First ctypes object.
        obj2: Second ctypes object.

    Returns:
        True if all fields are equal, False otherwise.
    """
    if type(obj1) is not type(obj2):
        return False  # Objects must be of the same type

    if not isinstance(obj1, ctypes.Structure):
        return False

    from typing import cast

    obj1 = cast(ctypes.Structure, obj1)
    obj2 = cast(ctypes.Structure, obj2)

    for field_info in obj1._fields_:
        field_name, field_type = field_info[:2]

        val1 = getattr(obj1, field_name)
        val2 = getattr(obj2, field_name)

        if issubclass(field_type, ctypes.Structure):  # Nested structure
            if not ctypes_objects_equal(val1, val2):
                return False
        elif isinstance(val1, ctypes.Array):  # Arrays need element-wise comparison
            if len(val1) != len(val2) or any(v1 != v2 for v1, v2 in zip(val1, val2)):
                return False
        else:  # Primitive types
            if val1 != val2:
                return False

    return True
