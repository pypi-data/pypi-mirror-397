# Copyright (C) 2024 Floating Rock Studio Ltd
from __future__ import annotations
import typing
import copy
import os
import re
from pathlib import Path
import pyjson5
from .base import ConfigBase
from ..core.path import find_configs
from ..core.resolver import (
    resolve_value_type_modifiers,
    flatten_modifiers,
    get_key_paths,
    resolve_default,
)
from ..core import validate
from ..utils.typing import ensure_list
from ..utils.logging import get_logger
from ... import constants
from ...interfaces import IConfigLoader

_LOG = get_logger("fr_config")

_STR_REPLACE = {constants.PATHSEP_TOKEN: os.pathsep}


def _format_str(s: str) -> str:
    for k, v in _STR_REPLACE.items():
        s = s.replace(k, v)
    return s


class ConfigLoader(ConfigBase, IConfigLoader):
    """Initializes a config
    Args:
        name(str): Config name
        context(Context): Context or path to load configs from
        variants(str|List[str]): variant(s) to load, defaults to constants.KEYS.DEFAULT
        tags(List[str]): Optional tags to load, defaults to published,latest, order is important
        cascsade(bool): Load configs in a hierarchical cascade with top level configs loading first
        continue_on_error(bool): If a config in the stack is not valid, this will allow to load the remaining valid
                                 configs. Use this only when failing to resolve the config causes more propblems
    """

    def __init__(
        self,
        name: str,
        path: typing.Union[str, Path],
        variant: typing.Union[typing.List[str], str, None] = None,
        tags: typing.Union[str, typing.List[str]] = None,
        load: bool = True,
        cascade: bool = True,
        continue_on_error: bool = False,
    ):
        super().__init__(name=name, path=path, variant=variant, tags=tags)
        self.__loaded_defaults = False
        self.__loaded_paths = []
        self._data = {}
        if load:
            self.load(self._path, cascade=cascade, continue_on_error=continue_on_error)

    # MARK: load()
    def load(
        self,
        path: typing.Union[str, Path],
        variant: typing.Union[typing.List[str], str] = None,
        tags: typing.Union[str, typing.List[str]] = None,
        cascade: bool = True,
        continue_on_error: bool = False,
    ) -> ConfigLoader:
        """Load the config at the specified context
        Args:
            context(Context): Context or path to load configs from
            variants(str|List[str]): variant(s) to load, defaults to constants.DEFAULT_VARIANT
            tags(List[str]): Optional tags to load, defaults to published,latest, order is important
            cascsade(bool): Load configs in a hierarchical cascade with top level configs loading first
            continue_on_error(bool): If a config in the stack is not valid, this will allow to load the remaining valid
                                    configs. Use this only when failing to resolve the config causes more propblems
        """
        path = Path(path)
        if variant:
            variants = (
                ensure_list(variant)
                if isinstance(variant, (list, tuple, set))
                else [variant, constants.DEFAULT_VARIANT]
            )
        else:
            variants = self.variants
        if tags:
            tags = ensure_list(tags)
        else:
            tags = self.tags

        configs = find_configs(path, self.name, variant=variants, tags=tags, cascade=cascade)
        for path in configs[::-1]:
            _LOG.debug("Loading Config %s", path.as_posix())
            try:
                self._load_config(path, continue_on_error=continue_on_error)
            except Exception as e:
                _LOG.exception("Unhandled Exception %s", path.as_posix())
                if continue_on_error:
                    continue
                raise e
            self.__loaded_paths.append(path)

        return self

    def loaded_paths(self) -> typing.List[Path]:
        return copy.copy(self.__loaded_paths)

    def _load_config(self, path: Path, continue_on_error: bool = False):
        try:
            with path.open("r", encoding="UTF-8") as f:
                data = pyjson5.load(f)
        except pyjson5.Json5Exception as e:
            _LOG.exception("Failed to parse config %s", path.as_posix())
            if continue_on_error:
                return
            raise e

        try:
            # validate against the fr_schema
            validate.validate(data, self._schema, name=self._name)
        except validate.DataValidationException as e:
            _LOG.exception("Failed to validate config %s", path.as_posix())
            if continue_on_error:
                return
            raise e

        # cascade the data accordingly
        if not self.__loaded_defaults:
            self._load_defaults()
            self.__loaded_defaults = True

        for k, v in data.items():
            schema = self._schema.get(k)
            if not schema:
                continue
            self._data[k] = self._resolve(f"/{k}", self._data[k], v, schema)

    def __resolve_compare(self, values, compare_expr):
        result = []
        if values is None:
            return result
        for each in values:
            if match := compare_expr.match(each):
                result.append(match.groups())
            else:
                result.append(None)

        return result

    # MARK: _resolve()

    def _resolve(self, key_path: str, current_value, new_value, schema):
        """Internally resolve this value against the current
        This assumes the value has passed validation

        Args:
            key_path(str): /key/subkey, for depth tracking
            current_value(Any): value already set
            new_value(Any): new value to resolve
            schema(dict): schema for this value

        Returns:
            resolved value
        """
        # TODO: support for negated keys and nested negated keys: !variables, tools/!packages[]
        type_ = schema.get(constants.KEYS.TYPE, constants.TYPES.OBJECT)
        schema, new_value = resolve_value_type_modifiers(type_, new_value, schema)

        cascade = schema.get(constants.KEYS.CASCADE_MODE, constants.CASCADE.REPLACE)
        unique = schema.get(constants.KEYS.UNIQUE, False)

        if type_ not in (constants.TYPES.ARRAY, constants.TYPES.STRING, constants.TYPES.OBJECT):
            # only list/string/dict can be cascaded currently.
            # Note, once negation is in place this will need to check and remove any nested negated entries
            return flatten_modifiers(type_, new_value, schema)

        if type_ == constants.TYPES.STRING:
            separator = schema.get(constants.KEYS.SEPARATOR, {constants.KEYS.DEFAULT: ""})[constants.KEYS.DEFAULT]
            compare = schema.get(constants.KEYS.COMPARE)
            if isinstance(new_value, dict):
                if constants.KEYS.CASCADE_MODE in new_value:
                    cascade = new_value[constants.KEYS.CASCADE_MODE]
                if constants.KEYS.SEPARATOR in new_value:
                    separator = new_value[constants.KEYS.SEPARATOR]
                if constants.KEYS.COMPARE in new_value:
                    compare = new_value[constants.KEYS.COMPARE]
                new_value = new_value[constants.KEYS.VALUE]
            new_value = _format_str(new_value)

            if cascade in (constants.CASCADE.REPLACE, constants.CASCADE.UPDATE):
                return flatten_modifiers(type_, new_value, schema)

            separator = _format_str(separator)
            if unique:
                values = current_value.split(separator) if separator else [current_value]
                new_values = new_value.split(separator) if separator else [new_value]
                if compare:
                    compare_expr = re.compile(compare)  # todo: validate
                    current_compare = self.__resolve_compare(values, compare_expr)
                    replace = []
                    append = []
                    for each in new_values:
                        if each in values:
                            continue
                        if match := compare_expr(each):
                            if match.groups() in current_compare:
                                replace.append((current_compare.index(match.groups()), each))
                            continue
                        append.append(each)

                    for i, each in replace:
                        values[i] = each
                    if cascade == constants.CASCADE.PREPEND:
                        values = append + values
                    else:
                        values += append
                    return separator.join(values)
                else:
                    return separator.join(values + [v for v in new_values if v not in values])

            if cascade == constants.CASCADE.PREPEND:
                return separator.join((new_value, current_value))
            if cascade in constants.CASCADE.APPEND:
                return separator.join((current_value, new_value))

            # unsupported cascade mode
            return new_value

        # list or dict
        item_schema = schema.get(constants.KEYS.ITEMS, {})
        item_type = item_schema.get(constants.KEYS.TYPE, constants.TYPES.OBJECT)

        if type_ == constants.TYPES.ARRAY:
            if cascade == constants.CASCADE.REPLACE:
                return flatten_modifiers(type_, new_value, item_schema)

            if current_value is None:
                current_value = []
            replace = []
            append = []
            if not item_schema.get(constants.KEYS.COMPARE) or item_type != constants.TYPES.STRING:
                # Simple comparison
                for each in new_value:
                    each_item_schema, each_value = resolve_value_type_modifiers(item_type, each, item_schema)
                    # We aren't checking post this currently for arrays of complex types
                    each_value = flatten_modifiers(item_type, each_value, each_item_schema)

                    if (unique and each_value not in current_value) or not unique:
                        append.append(each_value)

            else:
                # 'unique' is implied if there is a compare
                # Compare is only valid for string types
                compare_expr = re.compile(item_schema[constants.KEYS.COMPARE][constants.KEYS.DEFAULT])  # todo: validate
                current_compare = self.__resolve_compare(current_value, compare_expr)
                # Treat each add individually
                for i, each in enumerate(new_value):
                    each_item_schema, each_value = resolve_value_type_modifiers(item_type, each, item_schema)
                    # We aren't checking post this currently for arrays of complex types
                    each_value = flatten_modifiers(item_type, each_value, each_item_schema)
                    if each_value in current_value:
                        continue
                    if match := compare_expr.match(each_value):
                        if match.groups() in current_compare:
                            replace.append((current_compare.index(match.groups()), each_value))
                            continue
                    append.append(each_value)

            values = copy.copy(current_value)
            for i, each in replace:
                values[i] = each
            if cascade == constants.CASCADE.PREPEND:
                values = append + values
            else:
                values += append

            return values

        if type_ == constants.TYPES.OBJECT:
            # 'unique' is ingored for object, all keys are unique anyway
            if item_type == constants.TYPES.STRING:
                if item_schema.get(constants.KEYS.COMPARE):
                    compare_expr = re.compile(
                        item_schema[constants.KEYS.COMPARE][constants.KEYS.DEFAULT]
                    )  # todo: validate
                    # compare dict values, value here is string
                    for key, value in new_value.items():
                        each_item_schema, each_value = resolve_value_type_modifiers(item_type, value, item_schema)
                        each_value = flatten_modifiers(item_type, each_value, each_item_schema)
                        if key not in current_value:
                            current_value[key] = _format_str(each_value)
                        else:
                            # separator = _format_str(each_item_schema.get(constants.KEYS.SEPARATOR, ""))
                            cascade = each_item_schema.get(constants.KEYS.CASCADE_MODE, constants.CASCADE.REPLACE)

                            new_compare = self.__resolve_compare(each_value, compare_expr)
                            current_compare = self.__resolve_compare(current_value[key], compare_expr)
                            if current_compare == new_compare:
                                current_value[key] = each_value
                else:
                    for key, value in new_value.items():
                        each_item_schema, each_value = resolve_value_type_modifiers(item_type, value, item_schema)
                        each_value = _format_str(flatten_modifiers(item_type, each_value, each_item_schema))
                        if key not in current_value:
                            current_value[key] = each_value
                        else:
                            cascade = each_item_schema.get(constants.KEYS.CASCADE_MODE, constants.CASCADE.REPLACE)

                            if cascade == constants.CASCADE.REPLACE:
                                current_value[key] = each_value

                            # append or replace
                            current_value[key] = self._resolve(
                                f"{key_path}/{key}", current_value[key], each_value, each_item_schema
                            )

            else:
                # Simple comparison
                for k, v in new_value.items():
                    if item_type in (None, constants.TYPES.OBJECT) and item_schema:
                        schema_ = item_schema.get(k, item_schema)
                    else:
                        schema_ = item_schema or schema.get(k, {})
                    if k not in current_value:
                        current_value[k] = copy.deepcopy(resolve_default(schema_))
                    current_value[k] = self._resolve(
                        f"{key_path}/{k}",
                        current_value[k],
                        v,
                        schema_,
                    )
        return current_value

    def _load_defaults(self):
        # Load the defaults from the schema
        for k, v in self._schema.items():
            if k in constants.KEYS.PROTECTED or k.startswith("__"):
                continue
            self._data[k] = copy.deepcopy(resolve_default(v))

    def keys(self) -> typing.List[str]:
        return list(self._data.keys())

    def key_paths(self) -> typing.List[str]:
        return list(get_key_paths(self._data, self._schema))

    def resolve_to(self, key_path: str, value):
        """Given another value, use this as a base and resolve to it."""
        base = self.value(key_path)
        schema = self._get_schema(key_path)
        return self._resolve(key_path, base, value, schema)

    def static_resolve_value(self, key_path: str, base, value):
        """Resolves a value using the schema for a given path."""
        schema = self._get_schema(key_path)
        return self._resolve(key_path, base, value, schema)

    _SENTINEL = object()

    def value(self, key_path: str, default=_SENTINEL):
        if not key_path.startswith("/"):
            key_path = f"/{key_path}"

        schema = self._schema
        data = self._data
        keys = key_path.strip("/").split("/")
        for k in keys[0:-1]:
            if not k:
                continue  # Double slash //
            if constants.KEYS.ITEMS in schema:
                schema = schema[constants.KEYS.ITEMS]
            else:
                if k not in schema:
                    if default is not self._SENTINEL:
                        return default
                    raise RuntimeError(f"Failed to find path in schema: {key_path}")
                schema = schema[k]

            if k not in data:
                # Set default if dictionary
                type_ = schema[constants.KEYS.TYPE]
                if type_ == constants.TYPES.OBJECT:
                    data[k] = {}
            data = data[k]

        if keys[-1] in data:
            return data[keys[-1]]
        # Default?
        # TODO: Move the below to generics
        if constants.KEYS.ITEMS in schema:
            schema = schema[constants.KEYS.ITEMS]
        else:
            if keys[-1] not in schema:
                if default is not self._SENTINEL:
                    return default
                raise RuntimeError(f"Failed to find path in schema: {key_path}")
            schema = schema[keys[-1]]
        return self._schema_default(schema)
