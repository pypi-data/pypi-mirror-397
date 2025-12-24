from __future__ import annotations
import json
from typing import TextIO, cast

from ids_peak_common.serialization.iarchive import IArchive
from ids_peak_icv.exceptions import IOException
from ids_peak_icv.serialization.archive import Archive
from ids_peak_icv.exceptions import NotSupportedException, CorruptedException
from ids_peak_icv.serialization.serializer import SerializationType


class Deserializer:
    """
    A deserializer that reads serialized data and reconstructs
    IArchive objects.

    Currently, only JSON is supported.

    Example::

        deserializer = Deserializer()
        with open("input.json", "r") as f:
            archive = deserializer.read(f)
        archive.get("id", int) # 42
        archive.get("name", str) # 'example'

    .. versionadded:: ids_peak_icv 1.0
    .. ingroup:: ids_peak_icv_python_serialization
    """

    def __init__(self, serialization_type: SerializationType = SerializationType.JSON) -> None:
        """
        Initializes a deserializer instance.

        :param serialization_type: The format to use for deserialization.
                                   Defaults to :class:`SerializationType.JSON`.

        .. versionadded:: ids_peak_icv 1.0
        """
        self._type = serialization_type

    # -------------------------------------------------------------------------

    def read(self, stream: TextIO) -> IArchive:
        """
        Reads serialized data from the given text stream and returns
        a reconstructed IArchive.

        :param stream: The input stream to read from (e.g., file).
        :return: A new :class:`Archive` containing the deserialized data.
        :raises NotSupportedException: If the serialization format is unsupported
                                       or the JSON is invalid.
        :raises IOException: If the parsing fails.

        .. versionadded:: ids_peak_icv 1.0
        """
        if self._type != SerializationType.JSON:
            raise NotSupportedException(f"Serialization type {self._type} is not supported.")

        data = stream.read()
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            raise IOException(f"Failed to parse JSON: {e}")

        archive = Archive()
        self._populate_archive(archive, parsed)
        return archive

    # -------------------------------------------------------------------------

    def _populate_archive(self, archive: Archive, data: list | dict) -> None:
        """
        Recursively populates an Archive with parsed JSON data.

        :param archive: The archive to populate.
        :param data: Parsed JSON data (dict, list, scalar).
        :raises CorruptedException: If the format of the given data is invalid.
        """
        if not isinstance(data, dict):
            raise CorruptedException("Root of serialized data must be a JSON object.")

        for key, value in data.items():
            if isinstance(value, dict):
                nested = Archive()
                self._populate_archive(nested, value)
                archive.set(key, nested)
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    nested_list = []
                    for item in value:
                        nested = Archive()
                        self._populate_archive(nested, item)
                        nested_list.append(nested)
                    archive.set(key, cast(list[IArchive], nested_list))
                else:
                    archive.set(key, value)
            else:
                archive.set(key, value)
