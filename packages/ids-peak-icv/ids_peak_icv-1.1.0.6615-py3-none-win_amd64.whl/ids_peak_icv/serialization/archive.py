from __future__ import annotations

from typing import Any, Dict, List, Type, TypeAlias

from ids_peak_common.serialization.iarchive import IArchive
from ids_peak_icv.exceptions import NotSupportedException, CorruptedException


T: TypeAlias = IArchive.T

class Archive(IArchive):
    """
    A simple key-value store with type checking, similar to a dict.

    Supports only:
    - bool, int, float, str
    - IArchive
    - Lists of the above

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_serialization
    """
    AllowedValue = IArchive.AllowedValue | IArchive

    def __init__(self, data: Dict[str, Archive.AllowedValue] | None = None) -> None:
        if data is None:
            data = {}
        else:
            for key, value in data.items():
                self._validate_value(key, value)
        self._storage: Dict = data

    def set(self, key: str, value: AllowedValue) -> None:
        """
        Stores a value under the given key.

        :param key: Key to store the value under.
        :param value: The value to store (restricted types only).

        .. versionadded:: ids_peak_icv 1.0
        """
        self._validate_value(key, value)
        self._storage[key] = value

    def get(self, key: str, datatype: Type[T] | None) -> T:
        """
        Retrieves the value stored under the given key.

        :param key: Key of the value to retrieve.
        :param datatype: The expected datatype of the value.
                         If None is given, the type check is not executed.

        :raises CorruptedException: If the key is not found or the specified datatype is not the type of the stored value.

        :return: The stored value.

        .. versionadded:: ids_peak_icv 1.0
        """

        if key not in self._storage:
            raise CorruptedException(f"The specified key '{key}' is not in the archive.")

        value = self._storage[key]
        if datatype is not type(value) and datatype is not None:
            raise CorruptedException(f"The value of the specified key '{key}' is not of the expected datatype.")

        return value

    def get_archive(self, key: str) -> IArchive:
        """
        Retrieves the archive stored under the given key.

        :param key: Key of the archive to retrieve.

        :raises CorruptedException: If the key is not found or the specified datatype is not of type archive.

        :return: The stored archive.

        .. versionadded:: ids_peak_icv 1.0
        """

        if key not in self._storage:
            raise CorruptedException(f"The specified key '{key}' is not in the archive.")
        value = self._storage[key]
        if not isinstance(value, IArchive):
            raise CorruptedException(f"The value of the specified key '{key}' is not of the expected datatype.")

        return value

    def has(self, key: str) -> bool:
        """
        Checks whether a given key exists in the archive.

        :param key: The key to check.
        :return: True if the key exists, False otherwise.

        .. versionadded:: ids_peak_icv 1.0
        """
        return key in self._storage

    def keys(self) -> List[str]:
        """
        Returns all keys currently stored in the archive.

        :return: List of keys.

        .. versionadded:: ids_peak_icv 1.0
        """
        return list(self._storage.keys())

    def create_archive(self) -> IArchive:
        """
        Creates a new, empty archive instance.
        .. versionadded:: ids_peak_icv 1.0
        """
        return Archive()

    def __str__(self) -> str:
        """
        Human-readable string representation of the archive.

        .. versionadded:: ids_peak_icv 1.0
        """
        return str(self._storage)

    def __repr__(self) -> str:
        return f"Archive({str(self)})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Archive):
            return False

        if set(self._storage.keys()) != set(other._storage.keys()):
            return False

        for key in self._storage:
            if not self._compare_values(self._storage[key], other._storage[key]):
                return False

        return True

    def _compare_values(self, lhs: Any, rhs: Any) -> bool:
        if isinstance(lhs, Archive) and isinstance(rhs, Archive):
            return bool(lhs == rhs)

        if isinstance(lhs, list) and isinstance(rhs, list):
            if len(lhs) != len(rhs):
                return False
            return all(self._compare_values(val1, val2) for val1, val2 in zip(lhs, rhs))

        return bool(lhs == rhs)

    _ALLOWED_SCALARS = (bool, int, float, str, IArchive)

    def _validate_value(self, key: str, value: Any) -> None:
        """
        Ensures the provided value matches the allowed types.

        :param key: The key for which the value is being validated.
        :param value: The value to check.
        :raises NotSupportedException: If the type is not supported.
        """
        if isinstance(value, self._ALLOWED_SCALARS):
            return
        if isinstance(value, list):
            if len(value) == 0:
                return

            first_type = type(value[0])
            if all(isinstance(v, first_type) for v in value):
                if issubclass(first_type, self._ALLOWED_SCALARS):
                    return
        raise NotSupportedException(
            f"Unsupported value type for key '{key}': {type(value).__name__}"
        )
