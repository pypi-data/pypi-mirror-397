# typepack

Fast, safe binary serialization for Python supporting dataclasses, datetime, Decimal, UUID and custom types.

## Features

- **Zero dependencies** - uses only Python standard library
- **Safe** - no arbitrary code execution (unlike pickle)
- **Compact** - 35-45% smaller than JSON
- **Native Python types** - datetime, Decimal, UUID, Enum, dataclass, NamedTuple
- **Extensible** - register custom types with `@typepack.register`
- **Streaming** - memory-efficient processing for large datasets
- **Optional C extension** - ~1.5x faster serialization
- **MessagePack-compatible** - interoperable binary format

## Installation

```bash
pip install typepack
```

## Quick Start

```python
import typepack

# Serialize
data = typepack.pack({"name": "Ana", "age": 30, "active": True})

# Deserialize
obj = typepack.unpack(data)
```

## Supported Types

| Type | Example |
|------|---------|
| `None` | `None` |
| `bool` | `True`, `False` |
| `int` | `-2^63` to `2^64-1` |
| `float` | IEEE 754 double |
| `str` | `"hello"` (UTF-8) |
| `bytes` | `b"\x00\x01"` |
| `list` | `[1, 2, 3]` |
| `dict` | `{"key": "value"}` |
| `tuple` | `(1, 2, 3)` |
| `set` | `{1, 2, 3}` |
| `frozenset` | `frozenset([1, 2])` |
| `datetime` | `datetime(2024, 1, 1)` |
| `date` | `date(2024, 1, 1)` |
| `time` | `time(12, 30)` |
| `timedelta` | `timedelta(days=1)` |
| `Decimal` | `Decimal("99.99")` |
| `UUID` | `UUID("...")` |
| `Enum` | `Color.RED` |
| `dataclass` | `@dataclass class User` |
| `NamedTuple` | `class Point(NamedTuple)` |

## Examples

### Native Python Types

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID
import typepack

order = {
    "id": UUID("12345678-1234-5678-1234-567812345678"),
    "amount": Decimal("99.99"),
    "created_at": datetime(2024, 12, 15, 14, 30, 0),
    "tags": {"new", "featured"},
    "items": (1, 2, 3),
}

data = typepack.pack(order)
restored = typepack.unpack(data)

assert restored["id"] == order["id"]
assert restored["amount"] == order["amount"]
```

### Dataclasses

```python
from dataclasses import dataclass
import typepack

@dataclass
class User:
    name: str
    age: int

user = User("Ana", 30)
data = typepack.pack(user)
restored = typepack.unpack(data)
# {'__dataclass__': 'User', '__module__': '__main__', 'name': 'Ana', 'age': 30}
```

### Custom Types

```python
import typepack

@typepack.register
class Money:
    def __init__(self, amount: int, currency: str):
        self.amount = amount
        self.currency = currency

    def __typepack_encode__(self):
        return {"amount": self.amount, "currency": self.currency}

    @classmethod
    def __typepack_decode__(cls, data):
        return cls(data["amount"], data["currency"])

money = Money(1000, "USD")
data = typepack.pack(money)
restored = typepack.unpack(data)  # Money(amount=1000, currency='USD')
```

### Streaming

```python
import typepack

# Write multiple objects to file
items = [{"id": i} for i in range(1000)]
with open("data.bin", "wb") as f:
    typepack.pack_stream(items, f)

# Read lazily (memory efficient)
with open("data.bin", "rb") as f:
    for item in typepack.unpack_stream(f):
        process(item)
```

## Size Comparison

```python
import json
import typepack

obj = {"name": "Ana", "age": 30, "active": True}

json_size = len(json.dumps(obj).encode())  # 42 bytes
pack_size = len(typepack.pack(obj))        # 27 bytes

# typepack: 36% smaller than JSON
```

## Performance

typepack includes an optional C extension for improved performance:

```python
import typepack

typepack.is_accelerated()     # True if C extension loaded
typepack.has_pybyteswriter()  # True if Python 3.15+ (PyBytesWriter API)
```

| Operation | C Extension | Pure Python |
|-----------|-------------|-------------|
| pack/unpack | ~1.5x faster | baseline |

## API Reference

### Core Functions

```python
typepack.pack(obj) -> bytes        # Serialize object
typepack.unpack(data) -> Any       # Deserialize bytes
```

### Streaming Functions

```python
typepack.pack_to(obj, file)        # Write single object to file
typepack.unpack_from(file) -> Any  # Read single object from file

typepack.pack_stream(items, file)  # Write multiple objects
typepack.unpack_stream(file)       # Iterate over objects (lazy)

typepack.pack_many(items) -> bytes # Serialize multiple to bytes
typepack.unpack_many(data) -> list # Deserialize all at once
typepack.iter_unpack(data)         # Iterate over bytes (lazy)
```

### Type Registration

```python
@typepack.register
class MyType:
    def __typepack_encode__(self): ...
    @classmethod
    def __typepack_decode__(cls, data): ...

typepack.clear_registry()          # Reset type registry
```

### Introspection

```python
typepack.is_accelerated() -> bool      # C extension loaded?
typepack.has_pybyteswriter() -> bool   # PyBytesWriter available?
```

## Binary Format

typepack uses MessagePack-compatible binary format:

| Type | Format |
|------|--------|
| fixint | `0x00` - `0x7F` |
| fixmap | `0x80` - `0x8F` |
| fixarray | `0x90` - `0x9F` |
| fixstr | `0xA0` - `0xBF` |
| nil | `0xC0` |
| false | `0xC2` |
| true | `0xC3` |
| float64 | `0xCB` + 8 bytes |
| uint/int | `0xCC` - `0xD3` |
| str | `0xD9` - `0xDB` |
| array | `0xDC` - `0xDD` |
| map | `0xDE` - `0xDF` |

## Comparison

| Feature | typepack | msgpack | pickle | json |
|---------|----------|---------|--------|------|
| Safe | Yes | Yes | **No** | Yes |
| Zero deps | Yes | No | Yes | Yes |
| Python types | Yes | Limited | Yes | Limited |
| Dataclasses | Yes | No | Yes | No |
| Compact | Yes | Yes | No | No |
| Streaming | Yes | Yes | No | No |

## License

MIT
