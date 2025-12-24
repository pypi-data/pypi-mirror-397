from enum import Enum


class ProcessingPolicy(Enum):
    """
    Specifies the processing policy.

    Defines how the image processing pipeline handles bit depth conversions
    during processing, balancing performance and image quality.

    Warning:
        Changing the processing policy during active processing may cause
        inconsistent results. Set the policy before starting image processing
        operations.

    See Also:
        - DefaultPipeline.processing_policy

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_pipeline_types
    """

    FAST = 1
    """Prefer speed.

    Reduces the bit depth of the input image at the earliest suitable stage
    if the target bit depth is lower. Prioritizes performance over image quality.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    BALANCED = 2
    """Balance speed and quality.

    Retains the original bit depth throughout processing until the final
    pixel format conversion. Provides a trade-off between performance and quality.
    
    .. versionadded:: ids_peak_icv 1.0
    """

    ENHANCED = 3
    """Prefer quality.

    Increases the bit depth of the input image for all processing steps,
    if the target bit depth is higher. Prioritizes improved image quality
    over performance.
    
    .. versionadded:: ids_peak_icv 1.0
    """
