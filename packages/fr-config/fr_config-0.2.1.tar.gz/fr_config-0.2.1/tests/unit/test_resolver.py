"""Tests for ConfigLoader static_resolve_value and base class methods."""

import tempfile
import os
from pathlib import Path
from fr_config import ConfigLoader
from fr_config._internal.core import resolver


def test_static_resolve_value_with_cascade():
    """Test static_resolve_value with cascading arrays."""
    # Create test config structure
    base_dir = Path(tempfile.mkdtemp())

    # Create schema
    schema_dir = base_dir / "schema"
    schema_dir.mkdir()

    packages_schema = schema_dir / "packages.fr_schema"
    packages_schema.write_text(
        """{
    __version__: 1,
    packages: {
        type: "array",
        cascade: "append",
        unique: true,
        items: {type: "string"}
    },
    variables: {
        type: "object",
        cascade: "update",
        items: {type: "string"}
    }
}"""
    )

    # Create config
    config_dir = base_dir / "project" / ".fr_config" / "packages" / "default"
    config_dir.mkdir(parents=True)

    config_file = config_dir / "v1.fr_config"
    config_file.write_text(
        """{
    packages: ["base-1.0", "shared-2.1"],
    variables: {
        "BASE_VAR": "base_value",
        "SHARED_VAR": "shared_value"
    }
}"""
    )

    # Set environment
    original_schema_path = os.environ.get("FR_CONFIG_SCHEMA_PATH", "")
    os.environ["FR_CONFIG_SCHEMA_PATH"] = str(schema_dir)

    try:
        # Load config
        config = ConfigLoader("packages", str(base_dir / "project"))

        # Test static_resolve_value with packages (array append)
        base_packages = ["base-1.0", "shared-2.1"]
        new_packages = ["child-1.5", "addon-0.8"]

        resolved = config.static_resolve_value("/packages", base_packages, new_packages)
        expected = ["base-1.0", "shared-2.1", "child-1.5", "addon-0.8"]
        assert resolved == expected

        # Test static_resolve_value with variables (object update)
        base_vars = {"BASE_VAR": "base_value", "SHARED_VAR": "shared_value"}
        new_vars = {"SHARED_VAR": "new_shared", "CHILD_VAR": "child_value"}

        resolved_vars = config.static_resolve_value("/variables", base_vars, new_vars)
        expected_vars = {
            "BASE_VAR": "base_value",
            "SHARED_VAR": "new_shared",  # Updated
            "CHILD_VAR": "child_value",  # Added
        }
        assert resolved_vars == expected_vars

    finally:
        os.environ["FR_CONFIG_SCHEMA_PATH"] = original_schema_path


def test_get_schema_method():
    """Test _get_schema method retrieves correct schema sections."""
    base_dir = Path(tempfile.mkdtemp())

    # Create schema with nested structure
    schema_dir = base_dir / "schema"
    schema_dir.mkdir()

    nested_schema = schema_dir / "nested.fr_schema"
    nested_schema.write_text(
        """{
    __version__: 1,
    render_settings: {
        type: "object",
        quality: {type: "string", default: "high"},
        resolution: {
            type: "object",
            width: {type: "int", default: 1920},
            height: {type: "int", default: 1080}
        }
    },
    tools: {
        type: "array",
        items: {
            type: "object",
            name: {type: "string"},
            version: {type: "string"}
        }
    }
}"""
    )

    # Create minimal config
    config_dir = base_dir / "project" / ".fr_config" / "nested" / "default"
    config_dir.mkdir(parents=True)

    config_file = config_dir / "v1.fr_config"
    config_file.write_text("{}")

    # Set environment
    original_schema_path = os.environ.get("FR_CONFIG_SCHEMA_PATH", "")
    os.environ["FR_CONFIG_SCHEMA_PATH"] = str(schema_dir)

    try:
        config = ConfigLoader("nested", str(base_dir / "project"))

        # Test getting top-level schema
        render_schema = config._get_schema("/render_settings")
        assert render_schema["type"] == "object"
        assert "quality" in render_schema

        # Test getting nested schema
        resolution_schema = config._get_schema("/render_settings/resolution")
        assert resolution_schema["type"] == "object"
        assert "width" in resolution_schema

        # Test getting deeply nested schema
        width_schema = config._get_schema("/render_settings/resolution/width")
        assert width_schema["type"] == "int"
        assert width_schema["default"] == 1920

        # Test schema for array items
        tools_schema = config._get_schema("/tools")
        assert tools_schema["type"] == "array"
        assert "items" in tools_schema

    finally:
        os.environ["FR_CONFIG_SCHEMA_PATH"] = original_schema_path


def test_schema_default_method():
    """Test _schema_default method generates correct defaults."""
    base_dir = Path(tempfile.mkdtemp())

    # Create schema with various default types
    schema_dir = base_dir / "schema"
    schema_dir.mkdir()

    defaults_schema = schema_dir / "defaults.fr_schema"
    defaults_schema.write_text(
        """{
    __version__: 1,
    explicit_default: {type: "string", default: "custom_value"},
    string_type: {type: "string"},
    int_type: {type: "int"},
    float_type: {type: "float"},
    bool_type: {type: "bool"},
    object_type: {type: "object"},
    array_type: {type: "array"},
    fixed_array: {
        type: "array",
        length: 3,
        items: {type: "int"}
    }
}"""
    )

    # Create minimal config
    config_dir = base_dir / "project" / ".fr_config" / "defaults" / "default"
    config_dir.mkdir(parents=True)

    config_file = config_dir / "v1.fr_config"
    config_file.write_text("{}")

    # Set environment
    original_schema_path = os.environ.get("FR_CONFIG_SCHEMA_PATH", "")
    os.environ["FR_CONFIG_SCHEMA_PATH"] = str(schema_dir)

    try:
        config = ConfigLoader("defaults", str(base_dir / "project"))

        # Test explicit default
        explicit_schema = config._get_schema("/explicit_default")
        assert config._schema_default(explicit_schema) == "custom_value"

        # Test type-based defaults
        string_schema = config._get_schema("/string_type")
        assert config._schema_default(string_schema) == ""

        int_schema = config._get_schema("/int_type")
        assert config._schema_default(int_schema) == 0

        float_schema = config._get_schema("/float_type")
        assert config._schema_default(float_schema) == 0.0

        bool_schema = config._get_schema("/bool_type")
        assert config._schema_default(bool_schema) == False

        object_schema = config._get_schema("/object_type")
        assert config._schema_default(object_schema) == {}

        array_schema = config._get_schema("/array_type")
        assert config._schema_default(array_schema) == []

        # Test fixed length array with typed items
        fixed_array_schema = config._get_schema("/fixed_array")
        assert config._schema_default(fixed_array_schema) == [0, 0, 0]

    finally:
        os.environ["FR_CONFIG_SCHEMA_PATH"] = original_schema_path


def test_resolve_refs():
    """Test resolve_refs function resolves $ref references."""
    schema = {"properties": {"name": {"$ref": "#/$defs/name_type"}, "settings": {"$ref": "#/$defs/settings_type"}}}

    defs = {
        "#/$defs/name_type": {"type": "string", "default": "untitled"},
        "#/$defs/settings_type": {"type": "object", "quality": {"type": "string"}, "enabled": {"type": "bool"}},
    }

    # Resolve references
    resolver.resolve_refs(schema, defs)

    # Check that references were resolved
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["name"]["default"] == "untitled"
    assert schema["properties"]["settings"]["type"] == "object"
    assert "quality" in schema["properties"]["settings"]
