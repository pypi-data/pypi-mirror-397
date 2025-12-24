import enum


class Rotation(enum.Enum):
    """
    Represents discrete rotation angles in degrees for use in rotation operations.

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_types
    """
    NO_ROTATION = 0
    """
    No rotation is applied (0 degrees).
    
    .. versionadded:: ids_peak_icv 1.0
    """

    DEGREE_90_COUNTERCLOCKWISE = 90
    """
    Rotate 90 degrees counterclockwise.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    DEGREE_180 = 180
    """
    Rotate 180 degrees (half turn).
    
    .. versionadded:: ids_peak_icv 1.0
    """

    DEGREE_90_CLOCKWISE = 270
    """
    Rotate 90 degrees clockwise.
    
    .. versionadded:: ids_peak_icv 1.0
    """
