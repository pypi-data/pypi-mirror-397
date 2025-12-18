"""Tests for pyuuid7 library."""

import re

import pyuuid7

UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


class TestUUID4:
    """Tests for UUID v4 generation."""

    def test_generates_valid_uuid(self):
        result = pyuuid7.uuid4()
        assert UUID_REGEX.match(result)

    def test_version_is_4(self):
        result = pyuuid7.uuid4()
        assert pyuuid7.get_version(result) == 4

    def test_generates_unique_values(self):
        uuids = [pyuuid7.uuid4() for _ in range(100)]
        assert len(set(uuids)) == 100


class TestUUID5:
    """Tests for UUID v5 generation."""

    DNS_NAMESPACE = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"

    def test_generates_valid_uuid(self):
        result = pyuuid7.uuid5(self.DNS_NAMESPACE, "example.com")
        assert result is not None
        assert UUID_REGEX.match(result)

    def test_version_is_5(self):
        result = pyuuid7.uuid5(self.DNS_NAMESPACE, "test")
        assert pyuuid7.get_version(result) == 5

    def test_is_deterministic(self):
        result1 = pyuuid7.uuid5(self.DNS_NAMESPACE, "test")
        result2 = pyuuid7.uuid5(self.DNS_NAMESPACE, "test")
        assert result1 == result2

    def test_different_names_produce_different_uuids(self):
        result1 = pyuuid7.uuid5(self.DNS_NAMESPACE, "name1")
        result2 = pyuuid7.uuid5(self.DNS_NAMESPACE, "name2")
        assert result1 != result2

    def test_invalid_namespace_returns_none(self):
        result = pyuuid7.uuid5("invalid", "test")
        assert result is None


class TestUUID7:
    """Tests for UUID v7 generation."""

    def test_generates_valid_uuid(self):
        result = pyuuid7.uuid7()
        assert UUID_REGEX.match(result)

    def test_version_is_7(self):
        result = pyuuid7.uuid7()
        assert pyuuid7.get_version(result) == 7

    def test_generates_unique_values(self):
        uuids = [pyuuid7.uuid7() for _ in range(100)]
        assert len(set(uuids)) == 100

    def test_is_time_sortable(self):
        uuids = [pyuuid7.uuid7() for _ in range(10)]
        assert uuids == sorted(uuids)


class TestValidation:
    """Tests for UUID validation functions."""

    def test_is_valid_with_valid_uuid(self):
        assert pyuuid7.is_valid("a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d")

    def test_is_valid_with_invalid_uuid(self):
        assert not pyuuid7.is_valid("invalid")
        assert not pyuuid7.is_valid("")
        assert not pyuuid7.is_valid("12345")

    def test_get_version_returns_correct_version(self):
        v4 = pyuuid7.uuid4()
        v7 = pyuuid7.uuid7()
        assert pyuuid7.get_version(v4) == 4
        assert pyuuid7.get_version(v7) == 7

    def test_get_version_invalid_returns_none(self):
        assert pyuuid7.get_version("invalid") is None

    def test_parse_normalizes_case(self):
        upper = "A1B2C3D4-E5F6-4A7B-8C9D-0E1F2A3B4C5D"
        result = pyuuid7.parse(upper)
        assert result == "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"

    def test_parse_invalid_returns_none(self):
        assert pyuuid7.parse("invalid") is None
