"""Test schema loading and ref resolution."""

from fr_config._internal.core.resolver import get_defs, resolve_refs


def test_get_defs_from_schema():
    """Test extracting $defs from schema."""
    schema = {
        "$defs": {
            "package_type": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+$"},
            "version_type": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
        },
        "packages": {"type": "array", "items": {"$ref": "#/$defs/package_type"}},
    }

    defs = get_defs(schema)

    assert "#/$defs/package_type" in defs
    assert defs["#/$defs/package_type"]["type"] == "string"
    assert "#/$defs/version_type" in defs
    assert defs["#/$defs/version_type"]["pattern"] == r"^\d+\.\d+\.\d+$"


def test_resolve_refs_recursive():
    """Test resolving nested $refs."""
    schema = {"tools": {"type": "array", "items": {"$ref": "#/$defs/tool"}}, "default_tool": {"$ref": "#/$defs/tool"}}

    defs = {
        "#/$defs/tool": {"type": "object", "name": {"$ref": "#/$defs/name_type"}, "version": {"type": "string"}},
        "#/$defs/name_type": {"type": "string", "default": "unknown"},
    }

    # Resolve refs
    resolve_refs(schema, defs)

    # Check top-level refs resolved
    assert schema["tools"]["items"]["type"] == "object"
    assert schema["default_tool"]["type"] == "object"

    # Check nested refs resolved
    assert schema["tools"]["items"]["name"]["type"] == "string"
    assert schema["tools"]["items"]["name"]["default"] == "unknown"
    assert schema["default_tool"]["name"]["type"] == "string"
    assert schema["default_tool"]["name"]["default"] == "unknown"
