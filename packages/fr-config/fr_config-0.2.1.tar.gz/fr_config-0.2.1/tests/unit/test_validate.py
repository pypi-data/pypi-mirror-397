"""Tests for the validate module."""

import pytest
from fr_config._internal.core import validate
from fr_config.exceptions import DataValidationException
from fr_config import constants


def test_validate_basic_types():
    """Test validation of basic data types."""
    schema = {
        "fps": {"type": "float"},
        "name": {"type": "string"},
        "enabled": {"type": "bool"},
        "count": {"type": "int"},
    }

    data = {"fps": 24.0, "name": "test", "enabled": True, "count": 5}

    # Should not raise any exception
    validate.validate(data, schema)


def test_validate_type_mismatch():
    """Test validation fails with type mismatch."""
    schema = {"fps": {"type": "float"}}

    data = {"fps": "not_a_number"}  # string instead of float

    with pytest.raises(DataValidationException, match="'fps' expected type 'float', got 'string'"):
        validate.validate(data, schema)


def test_validate_unknown_key():
    """Test validation fails with unknown key."""
    schema = {"fps": {"type": "float"}}

    data = {"fps": 24.0, "unknown_key": "value"}

    with pytest.raises(DataValidationException, match="'unknown_key' not in schema keys"):
        validate.validate(data, schema)


def test_validate_reserved_keys_ignored():
    """Test that reserved keys are ignored during validation."""
    schema = {"fps": {"type": "float"}}

    data = {
        "fps": 24.0,
        "$parent": "/some/path",  # Reserved key should be ignored
        "__info__": {"metadata": True},  # Reserved key should be ignored
    }

    # Should not raise any exception
    validate.validate(data, schema)


def test_validate_each_item_dict():
    """Test validation of each item in a dictionary."""
    schema = {"settings": {"type": "object", "each": {"quality": {"type": "string"}, "enabled": {"type": "bool"}}}}

    data = {"settings": {"quality": "high", "enabled": True}}

    # Should not raise any exception
    validate.validate(data, schema)


def test_validate_each_item_dict_invalid():
    """Test validation fails for invalid each item in dictionary."""
    schema = {"settings": {"type": "object", "each": {"quality": {"type": "string"}}}}

    data = {"settings": {"quality": 123}}  # Should be string

    with pytest.raises(DataValidationException, match="'quality' expected type 'string', got 'int'"):
        validate.validate(data, schema)


def test_validate_each_item_array():
    """Test validation of each item in an array."""
    schema = {"tools": {"type": "array", "each": {"type": "string"}}}

    data = {"tools": ["maya", "houdini", "nuke"]}

    # Should not raise any exception
    validate.validate(data, schema)


def test_validate_each_item_array_invalid():
    """Test validation fails for invalid each item in array."""
    schema = {"tools": {"type": "array", "each": {"type": "string"}}}

    data = {"tools": ["maya", 123, "nuke"]}  # Second item should be string

    with pytest.raises(DataValidationException, match="'tools' expected type 'string', got 'int'"):
        validate.validate(data, schema)


def test_validate_special_types():
    """Test validation with special types (custom type definitions)."""
    schema = {"packages": {"type": "package"}}

    special_types = {
        "package": {"value": {"type": "array"}, "compare": {"type": "string"}, "separator": {"type": "string"}}
    }

    data = {"packages": {"compare": "regex_pattern", "separator": ":"}}

    # Should not raise any exception
    validate.validate(data, schema, special_types)


def test_validate_special_types_invalid():
    """Test validation fails with invalid special type."""
    schema = {"packages": {"type": "package"}}

    special_types = {"package": {"value": {"type": "array"}, "compare": {"type": "string"}}}

    data = {"packages": {"compare": 123}}  # Should be string

    with pytest.raises(DataValidationException, match="'packages'.compare expected type 'string', got 'int'"):
        validate.validate(data, schema, special_types)


def test_validate_special_types_from_schema():
    """Test validation extracts special types from schema __types__ key."""
    schema = {
        "__types__": {"environ": {"value": {"type": "string"}, "separator": {"type": "string"}}},
        "PATH": {"type": "environ"},
    }

    data = {"PATH": {"value": "/usr/bin:/usr/local/bin", "separator": ":"}}

    # Should not raise any exception - special types extracted from schema
    validate.validate(data, schema)


def test_validate_nested_context():
    """Test validation provides proper context in error messages."""
    schema = {"nested": {"type": "object", "each": {"inner": {"type": "object", "each": {"value": {"type": "int"}}}}}}

    data = {"nested": {"inner": {"value": "not_an_int"}}}

    with pytest.raises(DataValidationException, match="'value' expected type 'int', got 'string'"):
        validate.validate(data, schema, name="test_config")
