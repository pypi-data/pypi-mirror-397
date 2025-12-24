from abc import ABC

from ids_peak_common.pipeline.modules.imodule import IModule
from ids_peak_common.serialization import IArchive
from ids_peak_icv.exceptions import NotSupportedException, CorruptedException


class ModuleBase(IModule, ABC):
    """
    Base class for all pipeline modules.

     .. ingroup:: ids_peak_icv_python_pipeline_modules
     .. versionadded:: ids_peak_icv 1.0
    """

    def __init__(self) -> None:
        """
        Creates an instance of class ModuleBase.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._enabled: bool = True

    # -------------------------------------------------------------------------
    @property
    def version(self) -> int:
        """
        Return the module version.

        :return: Module version.

        .. versionadded:: ids_peak_icv 1.0
        """
        return 1

    @property
    def enabled(self) -> bool:
        """
        Get whether this module is enabled.

        When disabled, `process` returns the input image unchanged.

        :return: True if the module is enabled, False otherwise.

        .. versionadded:: ids_peak_icv 1.0
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enable or disable the module.

        When disabled, `process` returns the input image unchanged.

        :param value: True to enable, False to disable.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._enabled = value

    # -------------------------------------------------------------------------

    def serialize(self, archive: IArchive) -> None:
        """
        Serializes the object's internal state into the provided archive.

        This function populates the given archive with all parameters required to fully represent the current state of the object.
        It ensures that the object can be reconstructed or transmitted accurately by saving all relevant data members
        in a consistent and structured format.

        :return: The serialized module's internal state.

        .. versionadded:: ids_peak_icv 1.0
        """
        archive.set("Enabled", self.enabled)
        archive.set("Version", self.version)

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
        self._validate_version(archive)
        self.enabled = archive.get("Enabled", bool)

    def _validate_version(self, archive: IArchive) -> None:
        archive_version = archive.get("Version", int)
        if archive_version > self.version or archive_version < 1:
            self._raise_version_is_not_supported(str(archive_version), str(self.version))

    # -------------------------------------------------------------------------

    def _raise_corrupted_archive_key_missing(self, missing_archive_key: str) -> None:
        raise CorruptedException(f"The given archive is corrupted. The key '{missing_archive_key}' is missing.")

    def _raise_version_is_not_supported(self, actual_version: str, expected_version: str) -> None:
        raise NotSupportedException(
            "The given version in the settings exceeds the module version. "
            f"Given settings version: {actual_version}, Module version: {self.version}. "
            "The module version has to be >= the given settings version.")
