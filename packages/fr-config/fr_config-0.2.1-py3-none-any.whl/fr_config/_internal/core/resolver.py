# Copyright (C) 2024 Floating Rock Studio Ltd
import copy
import typing
import os
from pathlib import Path
import pyjson5
import jsonschema
from ...exceptions import SchemaValidationException
from ... import constants

_FR_SCHEMA = None


def resolve_default(schema):
    if constants.KEYS.DEFAULT in schema:
        return schema[constants.KEYS.DEFAULT]
    if schema.get(constants.KEYS.TYPE, constants.TYPES.OBJECT) == constants.TYPES.OBJECT:
        default = {}
        for k, v in schema.items():
            if k in constants.KEYS.PROTECTED or k.startswith("__"):
                continue
            default[k] = resolve_default(v)
        return default
    if schema.get(constants.KEYS.TYPE) == constants.TYPES.ARRAY:
        return []
    return None


# MARK: Type Refs


def resolve_refs(d: typing.Any, defs: typing.Dict[str, typing.Any], depth: int = 0, maxdepth: int = 5):
    """Resolves any $ref tags in a json schema
    This is due to $refs not currently being supported by pyjsonschema

    Args:
        d(dict): value to modify
        defs(dict): map of defined references
        depth(int): current recursion depth
        maxdepth(int): max recursion depth
    """
    if not isinstance(d, dict):
        return
    ref = d.get("$ref", None)
    if ref:
        value = defs[ref]
        if depth < maxdepth:
            resolve_refs(value, defs, depth=depth + 1, maxdepth=maxdepth)
        d.clear()
        d.update(copy.deepcopy(value))
    else:
        for _k, v in d.items():
            resolve_refs(v, defs, depth=depth, maxdepth=maxdepth)


def get_defs(schema: typing.Dict[str, typing.Any]):
    """get the defs from a schema

    Args:
        schema(dict)

    Returns:
        dict[str, dict]
    """
    return {f"#/$defs/{k}": v for k, v in schema.get("$defs", {}).items()}


def resolve_type_references(d: typing.Any, types: typing.Dict[str, typing.Any], depth: int = 0, maxdepth: int = 5):
    """Resolves any $ref tags in a json schema
    This is due to $refs not currently being supported by pyjsonschema

    Args:
        d(dict): value to modify
        defs(dict): map of defined references
        depth(int): current recursion depth
        maxdepth(int): max recursion depth
    """
    if not isinstance(d, dict):
        return
    type_ = d.get(constants.KEYS.TYPE, None)
    if type_ and type_ in types:
        type_info = types[type_]
        if depth < maxdepth:
            resolve_type_references(type_info, types, depth=depth + 1, maxdepth=maxdepth)
        d.update(copy.deepcopy(type_info))
    else:
        for _k, v in d.items():
            resolve_type_references(v, types, depth=depth, maxdepth=maxdepth)


# MARK: Load Schema


def load_schema(path: typing.Union[str, Path]):
    """Loads and preprocesses a schema

    Args:
        path(str|Path): path to schema file

    Returns:
        dict: schema

    Raises:
        SchemaValidationException: If schema is not valid
    """
    path = Path(path)
    with path.open("r", encoding="UTF-8") as f:
        data = pyjson5.load(f)

    # Validate the schema
    global _FR_SCHEMA
    if _FR_SCHEMA is None:
        fr_schema_path = constants.CORE_SCHEMA_PATH
        if not fr_schema_path.exists():
            raise RuntimeError(f"fr_config not installed correctly, schema not found at: {fr_schema_path}")

        with fr_schema_path.open("r", encoding="UTF-8") as f:
            _FR_SCHEMA = pyjson5.load(f)

            defs = get_defs(data)
            if defs:
                # Resolve any recursive references
                resolve_refs(defs, defs)
                resolve_refs(_FR_SCHEMA, defs)

    if _FR_SCHEMA:
        try:
            jsonschema.validate(data, schema=_FR_SCHEMA)
        except jsonschema.ValidationError as e:
            raise SchemaValidationException(f"Schema is invalid at {path}") from e
        except jsonschema.SchemaError as e:
            fr_schema_path = constants.CORE_SCHEMA_PATH
            raise SchemaValidationException(f"fr_config core schema is invalid at {fr_schema_path}") from e

    type_references = data.pop("__types__", {})
    if type_references:
        # Resolve any recursive references
        resolve_type_references(type_references, type_references)
        resolve_type_references(data, type_references)
    return data


# MARK: Modifiers


def resolve_value_type_modifiers(type_, value, schema):
    if type_ != constants.TYPES.OBJECT and isinstance(value, dict) and constants.KEYS.VALUE in value:
        actual_value = value.pop(constants.KEYS.VALUE)
        schema = copy.deepcopy(schema)
        schema.update(value)
        return (schema, actual_value)
    return (schema, value)


def flatten_modifiers(type_, value, schema):
    if type_ is None:
        type_ = infer_type(value)
    if type_ == constants.TYPES.ARRAY:
        # TODO: Check against schema rather then infer
        schema = schema.get(constants.KEYS.ITEMS, schema)
        return [flatten_modifiers(infer_type(v), v, schema) for v in value]
    elif type_ == constants.TYPES.OBJECT and isinstance(value, dict):
        return {k: flatten_modifiers(infer_type(v), v, schema.get(k, schema)) for k, v in value.items()}
    return resolve_value_type_modifiers(type_, value, schema)[1]


def infer_type(value):
    return constants.TYPE_MAP.get(type(value).__name__, constants.TYPES.OBJECT)


def get_key_paths(data, schema, parent="") -> typing.Generator:
    """Get all key paths in a nested dictionary based on a schema
    Args:
        data(dict): data to traverse
        schema(dict): schema to traverse
        parent(str): parent path
    Yields:
        str: key path
    """
    for k, v in schema.items():
        if k in constants.KEYS.PROTECTED or k.startswith("__"):
            continue
        yield f"{parent}/{k}"
        type_ = v.get(constants.KEYS.TYPE)
        if type_ == constants.TYPES.OBJECT:
            if constants.KEYS.ITEMS in v and k in data:
                item_schema = v[constants.KEYS.ITEMS]
                item_type = item_schema.get(constants.KEYS.TYPE)
                for each_key, each_value in data[k].items():
                    yield f"{parent}/{k}/{each_key}"
                    if item_type in (constants.TYPES.OBJECT, constants.TYPES.ARRAY):
                        yield from get_key_paths(each_value, item_schema, f"{parent}/{k}/{each_key}")


def set_dict_path(d, path, value, separator="/"):
    """Set a value in a nested dictionary using a path
    Args:
        d(dict): dictionary to modify
        path(str): path to set
        value: value to set
        separator(str): separator for path, default "/"
    """
    items = path.strip(separator).split(separator)
    if len(items) == 1:
        d[items[0]] = value
        return
    for item in items[:-1]:
        if item not in d:
            d[item] = {}
        d = d[item]

    d[items[-1]] = value
