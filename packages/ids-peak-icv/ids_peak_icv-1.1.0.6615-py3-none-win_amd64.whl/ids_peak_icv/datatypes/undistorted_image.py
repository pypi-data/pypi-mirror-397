from typing import Union

from ids_peak_ipl import ids_peak_ipl

from ids_peak_icv import lib_loader
from ids_peak_icv.backend.utils import execute_and_map_return_codes
from ids_peak_icv.datatypes.image import Image, _check_and_get_icv_image
from ids_peak_icv.calibration.intrinsic_parameters import IntrinsicParameters


class UndistortedImage(Image):
    """
    The UndistortedImage class is a class derived from the Image class.
    It encapsulates the result of a undistortion operation.
    During the undistortion process, new intrinsic parameters are calculated.
    These parameters are integral to the undistorted image and are
    required for any further processing or analysis, such as point cloud generation.

    .. ingroup:: ids_peak_icv_python_types
    .. versionadded:: ids_peak_icv 1.1
    """

    def __init__(self, image: Union[Image, ids_peak_ipl.Image],
                 intrinsic_parameters: IntrinsicParameters) -> None:
        """
        Creates an instance of UndistortedImage using an image and intrinsic parameters

        :param image: Depth map with radial coordinates.
        :param intrinsic_parameters: Intrinsic parameters derived from a camera calibration.

        .. versionadded:: ids_peak_icv 1.1
        """
        _image = _check_and_get_icv_image(image)

        super().__init__(_handle=_image._handle)

        execute_and_map_return_codes(lib_loader.dll().peak_icv_Image_IncreaseUseCount,
                                     _image._handle)

        self.intrinsic_parameters = intrinsic_parameters
