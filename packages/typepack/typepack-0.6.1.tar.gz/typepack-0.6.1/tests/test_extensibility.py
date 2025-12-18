"""Tests for typepack extensibility features (v0.3.0)."""

import pytest
from dataclasses import dataclass
from typing import NamedTuple

import typepack


class TestDataclass:
    """Tests for dataclass serialization."""

    def test_simple_dataclass(self):
        @dataclass
        class User:
            name: str
            age: int

        user = User("Ana", 30)
        data = typepack.pack(user)
        result = typepack.unpack(data)

        assert result["__dataclass__"] == "User"
        assert result["name"] == "Ana"
        assert result["age"] == 30

    def test_dataclass_with_optional(self):
        @dataclass
        class Product:
            name: str
            price: float
            description: str = None

        product = Product("Widget", 9.99)
        data = typepack.pack(product)
        result = typepack.unpack(data)

        assert result["__dataclass__"] == "Product"
        assert result["name"] == "Widget"
        assert result["price"] == 9.99
        assert result["description"] is None

    def test_dataclass_with_nested_types(self):
        @dataclass
        class Address:
            street: str
            city: str

        @dataclass
        class Person:
            name: str
            address: dict  # Nested as dict since Address won't be reconstructed

        address = Address("123 Main St", "Springfield")
        person = Person("John", {"street": "123 Main St", "city": "Springfield"})

        data = typepack.pack(person)
        result = typepack.unpack(data)

        assert result["__dataclass__"] == "Person"
        assert result["name"] == "John"
        assert result["address"]["street"] == "123 Main St"

    def test_dataclass_with_list(self):
        @dataclass
        class Order:
            id: int
            items: list

        order = Order(123, ["apple", "banana", "cherry"])
        data = typepack.pack(order)
        result = typepack.unpack(data)

        assert result["__dataclass__"] == "Order"
        assert result["id"] == 123
        assert result["items"] == ["apple", "banana", "cherry"]


class TestNamedTuple:
    """Tests for NamedTuple serialization."""

    def test_simple_namedtuple(self):
        class Point(NamedTuple):
            x: int
            y: int

        point = Point(10, 20)
        data = typepack.pack(point)
        result = typepack.unpack(data)

        assert result["__namedtuple__"] == "Point"
        assert result["x"] == 10
        assert result["y"] == 20

    def test_namedtuple_with_defaults(self):
        class Config(NamedTuple):
            host: str
            port: int = 8080

        config = Config("localhost")
        data = typepack.pack(config)
        result = typepack.unpack(data)

        assert result["__namedtuple__"] == "Config"
        assert result["host"] == "localhost"
        assert result["port"] == 8080

    def test_namedtuple_with_mixed_types(self):
        class Record(NamedTuple):
            id: int
            name: str
            active: bool
            score: float

        record = Record(1, "Test", True, 95.5)
        data = typepack.pack(record)
        result = typepack.unpack(data)

        assert result["__namedtuple__"] == "Record"
        assert result["id"] == 1
        assert result["name"] == "Test"
        assert result["active"] is True
        assert result["score"] == 95.5


class TestRegister:
    """Tests for @typepack.register decorator."""

    def setup_method(self):
        """Clear registry before each test."""
        typepack.clear_registry()

    def test_register_with_custom_encode_decode(self):
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

            def __eq__(self, other):
                return self.amount == other.amount and self.currency == other.currency

        money = Money(1000, "USD")
        data = typepack.pack(money)
        result = typepack.unpack(data)

        assert isinstance(result, Money)
        assert result.amount == 1000
        assert result.currency == "USD"

    def test_register_dataclass(self):
        @typepack.register
        @dataclass
        class Point3D:
            x: float
            y: float
            z: float

        point = Point3D(1.0, 2.0, 3.0)
        data = typepack.pack(point)
        result = typepack.unpack(data)

        assert isinstance(result, Point3D)
        assert result.x == 1.0
        assert result.y == 2.0
        assert result.z == 3.0

    def test_register_namedtuple(self):
        class Color(NamedTuple):
            r: int
            g: int
            b: int

        typepack.register(Color)

        color = Color(255, 128, 0)
        data = typepack.pack(color)
        result = typepack.unpack(data)

        assert isinstance(result, Color)
        assert result.r == 255
        assert result.g == 128
        assert result.b == 0

    def test_register_with_explicit_type_code(self):
        @typepack.register(type_code=0x30)
        class CustomType:
            def __init__(self, value: str):
                self.value = value

            def __typepack_encode__(self):
                return self.value

            @classmethod
            def __typepack_decode__(cls, data):
                return cls(data)

        obj = CustomType("test")
        data = typepack.pack(obj)
        result = typepack.unpack(data)

        assert isinstance(result, CustomType)
        assert result.value == "test"

    def test_duplicate_type_code_raises(self):
        @typepack.register(type_code=0x50)
        class TypeA:
            def __typepack_encode__(self):
                return {}

            @classmethod
            def __typepack_decode__(cls, data):
                return cls()

        with pytest.raises(ValueError, match="already registered"):
            @typepack.register(type_code=0x50)
            class TypeB:
                def __typepack_encode__(self):
                    return {}

                @classmethod
                def __typepack_decode__(cls, data):
                    return cls()

    def test_register_without_encode_decode_raises(self):
        with pytest.raises(TypeError, match="must have __typepack_encode__"):
            @typepack.register
            class InvalidType:
                pass


class TestMixedStructures:
    """Tests for complex structures with dataclasses and namedtuples."""

    def test_dict_with_dataclass(self):
        @dataclass
        class Item:
            name: str
            price: float

        item = Item("Coffee", 4.50)
        data = typepack.pack({"item": item, "quantity": 2})
        result = typepack.unpack(data)

        assert result["quantity"] == 2
        assert result["item"]["__dataclass__"] == "Item"
        assert result["item"]["name"] == "Coffee"
        assert result["item"]["price"] == 4.50

    def test_list_of_namedtuples(self):
        class Coord(NamedTuple):
            lat: float
            lng: float

        coords = [Coord(10.0, 20.0), Coord(30.0, 40.0)]
        data = typepack.pack(coords)
        result = typepack.unpack(data)

        assert len(result) == 2
        assert result[0]["__namedtuple__"] == "Coord"
        assert result[0]["lat"] == 10.0
        assert result[1]["lng"] == 40.0

    def test_dataclass_not_confused_with_dict(self):
        """Ensure dataclass is packed as ext, not as regular dict."""
        @dataclass
        class Config:
            debug: bool
            version: str

        config = Config(True, "1.0.0")
        regular_dict = {"debug": True, "version": "1.0.0"}

        config_data = typepack.pack(config)
        dict_data = typepack.pack(regular_dict)

        config_result = typepack.unpack(config_data)
        dict_result = typepack.unpack(dict_data)

        # Dataclass should have __dataclass__ marker
        assert "__dataclass__" in config_result
        assert "__dataclass__" not in dict_result

    def test_namedtuple_not_confused_with_tuple(self):
        """Ensure NamedTuple is packed as ext, not as regular tuple."""
        class Version(NamedTuple):
            major: int
            minor: int

        named = Version(1, 2)
        regular = (1, 2)

        named_data = typepack.pack(named)
        tuple_data = typepack.pack(regular)

        named_result = typepack.unpack(named_data)
        tuple_result = typepack.unpack(tuple_data)

        # NamedTuple should be a dict with __namedtuple__ marker
        assert isinstance(named_result, dict)
        assert "__namedtuple__" in named_result

        # Regular tuple should be a tuple
        assert isinstance(tuple_result, tuple)
