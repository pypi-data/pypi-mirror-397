from __future__ import annotations

import json
from typing import TextIO, cast, Any, Union, Dict, List

from ids_peak_common.serialization.iarchive import IArchive
from ids_peak_icv.exceptions import NotSupportedException
from ids_peak_icv.serialization.serialization_type import SerializationType
from ids_peak_icv.serialization.archive import Archive


class Serializer:
    """
    A serializer that converts IArchive objects into a textual
    representation.

    Currently, only JSON is supported.

    Example::

        from ids_peak_icv.serialization.archive import Archive
        archive = Archive()
        archive.set("name", "example")
        serializer = Serializer()
        with open("input.json", "w") as f:
            serializer.write(archive, f)

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_serialization
    """

    def __init__(self, serialization_type: SerializationType = SerializationType.JSON) -> None:
        """
        Initializes a new serializer with the given serialization type.

        :param serialization_type: The output serialization format.
                      Defaults to :class:`SerializationType.JSON`.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._type = serialization_type

    # -------------------------------------------------------------------------

    def write(self, archive: IArchive, stream: TextIO) -> None:
        """
        Serializes an IArchive object and writes it to the given stream.

        :param archive: The archive to serialize.
        :param stream: A writable text stream (e.g., file or StringIO).
        :raises NotSupportedException: If the configured serialization type is not supported.

        Example::

            archive = Archive()
            archive.set("id", 42)
            serializer = Serializer(SerializationType.JSON)
            with open("output.json", "w") as f:
                serializer.write(archive, f)

        .. versionadded:: ids_peak_icv 1.0
        """
        if self._type == SerializationType.JSON:
            data = self._to_dict(archive)
            json.dump(data, cast(Any, stream), ensure_ascii=False, indent=4)
        else:
            raise NotSupportedException(f"Serialization type {self._type} is not supported.")

    def _to_dict(self, archive: IArchive) -> dict:
        """
        Recursively converts an IArchive into a plain Python dict.

        :param archive: The archive to convert.
        :returns: A dictionary representation of the archive, suitable for serialization.

        .. versionadded:: ids_peak_icv 1.0
        """
        result: Dict[Any, Union[Dict[Any, Any], List[Dict[Any, Any]]]] = {}

        if not isinstance(archive, Archive):
            raise NotSupportedException("Serialization is only supported for the Archive implementation.")

        archive = cast(Archive, archive)
        for key in archive.keys():
            value = archive.get(key, None)
            if isinstance(value, IArchive):
                result[key] = self._to_dict(value)
            elif isinstance(value, list) and value and isinstance(value[0], IArchive):
                result[key] = [self._to_dict(v) for v in value]
            else:
                result[key] = value
        return result
