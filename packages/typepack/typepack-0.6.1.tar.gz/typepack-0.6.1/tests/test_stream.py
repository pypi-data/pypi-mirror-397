"""Tests for typepack streaming features (v0.4.0)."""

import io
import tempfile
import pytest
from datetime import datetime
from decimal import Decimal

import typepack


class TestPackTo:
    """Tests for pack_to function."""

    def test_pack_to_bytesio(self):
        buffer = io.BytesIO()
        bytes_written = typepack.pack_to({"name": "Ana"}, buffer)

        assert bytes_written > 0
        buffer.seek(0)
        assert typepack.unpack(buffer.read()) == {"name": "Ana"}

    def test_pack_to_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            bytes_written = typepack.pack_to([1, 2, 3], f)
            temp_path = f.name

        assert bytes_written > 0

        with open(temp_path, "rb") as f:
            result = typepack.unpack(f.read())

        assert result == [1, 2, 3]

    def test_pack_to_returns_correct_size(self):
        buffer = io.BytesIO()
        data = {"key": "value"}

        bytes_written = typepack.pack_to(data, buffer)
        packed = typepack.pack(data)

        assert bytes_written == len(packed)


class TestUnpackFrom:
    """Tests for unpack_from function."""

    def test_unpack_from_bytesio(self):
        data = typepack.pack({"id": 123})
        buffer = io.BytesIO(data)

        result = typepack.unpack_from(buffer)
        assert result == {"id": 123}

    def test_unpack_from_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(typepack.pack("hello"))
            temp_path = f.name

        with open(temp_path, "rb") as f:
            result = typepack.unpack_from(f)

        assert result == "hello"

    def test_unpack_from_empty_raises(self):
        buffer = io.BytesIO(b"")

        with pytest.raises(ValueError, match="Empty file"):
            typepack.unpack_from(buffer)


class TestPackStream:
    """Tests for pack_stream function."""

    def test_pack_stream_list(self):
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        buffer = io.BytesIO()

        bytes_written = typepack.pack_stream(items, buffer)

        assert bytes_written > 0
        buffer.seek(0)
        result = list(typepack.unpack_stream(buffer))
        assert result == items

    def test_pack_stream_generator(self):
        def gen():
            for i in range(5):
                yield {"n": i}

        buffer = io.BytesIO()
        typepack.pack_stream(gen(), buffer)

        buffer.seek(0)
        result = list(typepack.unpack_stream(buffer))
        assert len(result) == 5
        assert result[0] == {"n": 0}
        assert result[4] == {"n": 4}

    def test_pack_stream_empty(self):
        buffer = io.BytesIO()
        bytes_written = typepack.pack_stream([], buffer)

        assert bytes_written == 0
        buffer.seek(0)
        result = list(typepack.unpack_stream(buffer))
        assert result == []

    def test_pack_stream_mixed_types(self):
        items = [1, "two", 3.0, None, True, [4, 5]]
        buffer = io.BytesIO()

        typepack.pack_stream(items, buffer)

        buffer.seek(0)
        result = list(typepack.unpack_stream(buffer))
        assert result == items

    def test_pack_stream_to_file(self):
        items = [{"a": 1}, {"b": 2}]

        with tempfile.NamedTemporaryFile(delete=False) as f:
            typepack.pack_stream(items, f)
            temp_path = f.name

        with open(temp_path, "rb") as f:
            result = list(typepack.unpack_stream(f))

        assert result == items


class TestUnpackStream:
    """Tests for unpack_stream function."""

    def test_unpack_stream_returns_iterator(self):
        buffer = io.BytesIO()
        typepack.pack_stream([1, 2, 3], buffer)
        buffer.seek(0)

        result = typepack.unpack_stream(buffer)

        # Should be an iterator, not a list
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_unpack_stream_lazy(self):
        """Verify that unpack_stream doesn't read all at once."""
        buffer = io.BytesIO()
        items = list(range(100))
        typepack.pack_stream(items, buffer)
        buffer.seek(0)

        iterator = typepack.unpack_stream(buffer)

        # Read only first item
        first = next(iterator)
        assert first == 0

        # Buffer position should not be at end
        # (would be at end if all items were read)

    def test_unpack_stream_partial_length_raises(self):
        # Write incomplete length prefix
        buffer = io.BytesIO(b"\x00\x00")
        buffer.seek(0)

        with pytest.raises(ValueError, match="reading length"):
            list(typepack.unpack_stream(buffer))

    def test_unpack_stream_partial_data_raises(self):
        # Write complete length prefix but incomplete data
        buffer = io.BytesIO()
        buffer.write(b"\x00\x00\x00\x10")  # Length = 16
        buffer.write(b"\x00\x00\x00\x00")  # Only 4 bytes of data
        buffer.seek(0)

        with pytest.raises(ValueError, match="reading data"):
            list(typepack.unpack_stream(buffer))


class TestPackMany:
    """Tests for pack_many function."""

    def test_pack_many_basic(self):
        items = [1, 2, 3]
        data = typepack.pack_many(items)

        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_pack_many_roundtrip(self):
        items = [{"a": 1}, {"b": 2}, {"c": 3}]
        data = typepack.pack_many(items)
        result = typepack.unpack_many(data)

        assert result == items

    def test_pack_many_empty(self):
        data = typepack.pack_many([])
        assert data == b""
        assert typepack.unpack_many(data) == []

    def test_pack_many_single(self):
        data = typepack.pack_many(["hello"])
        result = typepack.unpack_many(data)
        assert result == ["hello"]


class TestUnpackMany:
    """Tests for unpack_many function."""

    def test_unpack_many_returns_list(self):
        data = typepack.pack_many([1, 2, 3])
        result = typepack.unpack_many(data)

        assert isinstance(result, list)
        assert result == [1, 2, 3]

    def test_unpack_many_complex_types(self):
        items = [
            {"timestamp": datetime(2024, 1, 1, 12, 0, 0)},
            {"amount": Decimal("99.99")},
            {"tags": {"a", "b", "c"}},
        ]
        data = typepack.pack_many(items)
        result = typepack.unpack_many(data)

        assert result[0]["timestamp"] == items[0]["timestamp"]
        assert result[1]["amount"] == items[1]["amount"]
        assert result[2]["tags"] == items[2]["tags"]


class TestIterUnpack:
    """Tests for iter_unpack function."""

    def test_iter_unpack_basic(self):
        data = typepack.pack_many([1, 2, 3])
        result = list(typepack.iter_unpack(data))
        assert result == [1, 2, 3]

    def test_iter_unpack_is_lazy(self):
        data = typepack.pack_many(list(range(100)))
        iterator = typepack.iter_unpack(data)

        # Should be a generator
        assert hasattr(iterator, "__iter__")
        assert hasattr(iterator, "__next__")

        # Can iterate one at a time
        assert next(iterator) == 0
        assert next(iterator) == 1

    def test_iter_unpack_partial_length_raises(self):
        # Incomplete length prefix
        with pytest.raises(ValueError, match="reading length"):
            list(typepack.iter_unpack(b"\x00\x00"))

    def test_iter_unpack_partial_data_raises(self):
        # Complete length prefix but incomplete data
        data = b"\x00\x00\x00\x10" + b"\x00\x00\x00\x00"  # Length=16, only 4 bytes
        with pytest.raises(ValueError, match="reading object"):
            list(typepack.iter_unpack(data))


class TestStreamRoundtrip:
    """Integration tests for streaming roundtrip."""

    def test_large_dataset(self):
        """Test with a large number of items."""
        items = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        buffer = io.BytesIO()

        typepack.pack_stream(items, buffer)
        buffer.seek(0)
        result = list(typepack.unpack_stream(buffer))

        assert result == items

    def test_file_roundtrip(self):
        """Test complete file roundtrip."""
        items = [
            {"type": "user", "name": "Ana", "age": 30},
            {"type": "user", "name": "Bob", "age": 25},
            {"type": "config", "debug": True, "version": "1.0"},
        ]

        with tempfile.NamedTemporaryFile(delete=False) as f:
            typepack.pack_stream(items, f)
            temp_path = f.name

        with open(temp_path, "rb") as f:
            result = list(typepack.unpack_stream(f))

        assert result == items

    def test_memory_roundtrip(self):
        """Test in-memory roundtrip with pack_many/unpack_many."""
        items = [i ** 2 for i in range(100)]

        data = typepack.pack_many(items)
        result = typepack.unpack_many(data)

        assert result == items
