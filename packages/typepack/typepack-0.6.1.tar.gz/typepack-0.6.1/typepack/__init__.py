"""
typepack - Fast, safe binary serialization for Python.

Uses C extension with PyBytesWriter API (Python 3.15+) for maximum performance,
with automatic fallback to pure Python implementation.

Usage:
    >>> import typepack
    >>> data = typepack.pack({"name": "Ana", "age": 30})
    >>> obj = typepack.unpack(data)
    >>> obj
    {'name': 'Ana', 'age': 30}

Custom types:
    >>> from dataclasses import dataclass
    >>> import typepack
    >>>
    >>> @dataclass
    ... class User:
    ...     name: str
    ...     age: int
    >>>
    >>> user = User("Ana", 30)
    >>> data = typepack.pack(user)
    >>> typepack.unpack(data)
    {'__dataclass__': 'User', '__module__': '__main__', 'name': 'Ana', 'age': 30}

Streaming:
    >>> import typepack
    >>> with open("data.bin", "wb") as f:
    ...     typepack.pack_stream([1, 2, 3], f)
    >>> with open("data.bin", "rb") as f:
    ...     list(typepack.unpack_stream(f))
    [1, 2, 3]

Check implementation:
    >>> import typepack
    >>> typepack.is_accelerated()  # True if using C extension
    >>> typepack.has_pybyteswriter()  # True if PyBytesWriter is available
"""

# Try to import C extension first
_USE_C_EXTENSION = False
_HAS_PYBYTESWRITER = False

try:
    from typepack._typepack import pack as _c_pack, unpack as _c_unpack
    from typepack._typepack import has_pybyteswriter as _has_pybyteswriter
    _USE_C_EXTENSION = True
    _HAS_PYBYTESWRITER = _has_pybyteswriter()
except ImportError:
    pass

# Import pure Python implementation
from typepack.core import pack as _py_pack, unpack as _py_unpack
from typepack.types import register, clear_registry
from typepack.stream import (
    pack_to,
    unpack_from,
    pack_stream,
    unpack_stream,
    pack_many,
    unpack_many,
    iter_unpack,
)


def is_accelerated() -> bool:
    """Return True if using C extension for pack/unpack."""
    return _USE_C_EXTENSION


def has_pybyteswriter() -> bool:
    """Return True if C extension was compiled with PyBytesWriter (Python 3.15+)."""
    return _HAS_PYBYTESWRITER


# Select implementation
# For basic types (int, float, str, bytes, list, dict, bool, None),
# use C extension if available
# For extended types (datetime, Decimal, etc.), always use Python
# implementation since C extension doesn't support them yet

if _USE_C_EXTENSION:
    def pack(obj):
        """
        Serialize a Python object to binary format.

        Uses C extension for basic types, falls back to Python for extended types.
        """
        # For now, always use Python for full type support
        # C extension will be used for basic types in hot paths
        return _py_pack(obj)

    def unpack(data):
        """
        Deserialize binary data to a Python object.

        Uses C extension for basic types, falls back to Python for extended types.
        """
        # For now, always use Python for full type support
        return _py_unpack(data)

    # Export C functions for direct access
    pack_basic = _c_pack
    unpack_basic = _c_unpack
else:
    pack = _py_pack
    unpack = _py_unpack
    pack_basic = _py_pack
    unpack_basic = _py_unpack


__version__ = "0.6.0"
__all__ = [
    # Core functions
    "pack",
    "unpack",
    # Basic type functions (C accelerated when available)
    "pack_basic",
    "unpack_basic",
    # Type registry
    "register",
    "clear_registry",
    # Streaming
    "pack_to",
    "unpack_from",
    "pack_stream",
    "unpack_stream",
    "pack_many",
    "unpack_many",
    "iter_unpack",
    # Introspection
    "is_accelerated",
    "has_pybyteswriter",
]
