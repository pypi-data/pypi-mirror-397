"""
Streaming serialization for typepack.

Provides functions to serialize/deserialize multiple objects
to/from file-like objects or iterators.
"""

import struct
from typing import Any, BinaryIO, Iterator, Iterable

from typepack.core import pack, _unpack_value


def pack_to(obj: Any, file: BinaryIO) -> int:
    """
    Serialize an object and write it to a file-like object.

    Args:
        obj: The Python object to serialize.
        file: A binary file-like object to write to.

    Returns:
        Number of bytes written.

    Example:
        >>> with open("data.bin", "wb") as f:
        ...     typepack.pack_to({"name": "Ana"}, f)
    """
    data = pack(obj)
    file.write(data)
    return len(data)


def unpack_from(file: BinaryIO) -> Any:
    """
    Read and deserialize a single object from a file-like object.

    Args:
        file: A binary file-like object to read from.

    Returns:
        The deserialized Python object.

    Raises:
        ValueError: If the data format is invalid or file is empty.

    Example:
        >>> with open("data.bin", "rb") as f:
        ...     obj = typepack.unpack_from(f)
    """
    data = file.read()
    if not data:
        raise ValueError("Empty file or end of stream")
    result, _ = _unpack_value(data, 0)
    return result


def pack_stream(objects: Iterable[Any], file: BinaryIO) -> int:
    """
    Serialize multiple objects to a file-like object.

    Each object is prefixed with its length (4 bytes, big-endian)
    to allow reading them back individually.

    Args:
        objects: An iterable of Python objects to serialize.
        file: A binary file-like object to write to.

    Returns:
        Total number of bytes written.

    Example:
        >>> items = [{"id": 1}, {"id": 2}, {"id": 3}]
        >>> with open("items.bin", "wb") as f:
        ...     typepack.pack_stream(items, f)
    """
    total_bytes = 0
    for obj in objects:
        data = pack(obj)
        # Write length prefix (4 bytes, big-endian)
        length_prefix = struct.pack(">I", len(data))
        file.write(length_prefix)
        file.write(data)
        total_bytes += 4 + len(data)
    return total_bytes


def unpack_stream(file: BinaryIO) -> Iterator[Any]:
    """
    Deserialize multiple objects from a file-like object.

    Expects objects to be prefixed with their length (4 bytes, big-endian)
    as written by pack_stream.

    Args:
        file: A binary file-like object to read from.

    Yields:
        Deserialized Python objects.

    Example:
        >>> with open("items.bin", "rb") as f:
        ...     for item in typepack.unpack_stream(f):
        ...         print(item)
    """
    while True:
        # Read length prefix
        length_bytes = file.read(4)
        if not length_bytes:
            # End of file
            break
        if len(length_bytes) < 4:
            raise ValueError("Unexpected end of stream while reading length")

        length = struct.unpack(">I", length_bytes)[0]

        # Read object data
        data = file.read(length)
        if len(data) < length:
            raise ValueError("Unexpected end of stream while reading data")

        result, _ = _unpack_value(data, 0)
        yield result


def iter_unpack(data: bytes) -> Iterator[Any]:
    """
    Iterate over multiple packed objects in a bytes buffer.

    Expects objects to be prefixed with their length (4 bytes, big-endian)
    as written by pack_stream.

    Args:
        data: Binary data containing multiple serialized objects.

    Yields:
        Deserialized Python objects.

    Example:
        >>> packed = pack_many([1, 2, 3])
        >>> list(iter_unpack(packed))
        [1, 2, 3]
    """
    offset = 0
    while offset < len(data):
        if offset + 4 > len(data):
            raise ValueError("Unexpected end of data while reading length")

        length = struct.unpack(">I", data[offset:offset + 4])[0]
        offset += 4

        if offset + length > len(data):
            raise ValueError("Unexpected end of data while reading object")

        result, _ = _unpack_value(data, offset)
        yield result
        offset += length


def pack_many(objects: Iterable[Any]) -> bytes:
    """
    Serialize multiple objects to a single bytes buffer.

    Each object is prefixed with its length (4 bytes, big-endian).

    Args:
        objects: An iterable of Python objects to serialize.

    Returns:
        Binary data containing all serialized objects.

    Example:
        >>> data = typepack.pack_many([{"id": 1}, {"id": 2}])
        >>> list(typepack.iter_unpack(data))
        [{'id': 1}, {'id': 2}]
    """
    buffer = bytearray()
    for obj in objects:
        data = pack(obj)
        # Write length prefix (4 bytes, big-endian)
        buffer.extend(struct.pack(">I", len(data)))
        buffer.extend(data)
    return bytes(buffer)


def unpack_many(data: bytes) -> list[Any]:
    """
    Deserialize multiple objects from a bytes buffer.

    Expects objects to be prefixed with their length (4 bytes, big-endian).

    Args:
        data: Binary data containing multiple serialized objects.

    Returns:
        List of deserialized Python objects.

    Example:
        >>> data = typepack.pack_many([1, 2, 3])
        >>> typepack.unpack_many(data)
        [1, 2, 3]
    """
    return list(iter_unpack(data))
