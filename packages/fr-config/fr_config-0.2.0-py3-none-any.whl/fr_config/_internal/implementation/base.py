# Copyright (C) 2024 Floating Rock Studio Ltd
from __future__ import annotations
from typing import List, Union
import copy
from pathlib import Path
from ..core.path import find_schema_path
from ..core.resolver import load_schema
from ..utils.typing import ensure_list
from ... import constants


class ConfigBase:
    """Base protocols for config access, used by config reader and writer"""

    def __init__(
        self,
        name: str,
        path: Union[str, Path],
        variant: Union[List[str], str, None] = None,
        tags: Union[str, List[str]] = None,
    ):
        self._name = name
        self._changes = {}
        self._schema_path = find_schema_path(name)
        self._schema = load_schema(self._schema_path)
        self._path = Path(path)
        if variant is None:
            self._variants = [constants.DEFAULT_VARIANT]
        else:
            self._variants = (
                ensure_list(variant)
                if isinstance(variant, (list, tuple, set))
                else [variant, constants.DEFAULT_VARIANT]
            )
        self._tags = ensure_list(tags) if tags else list(constants.TAGS.DEFAULT)

    def _get_schema(self, key_path: str):
        schema = self._schema
        keys = key_path.strip("/").split("/")
        for k in keys:
            if not k:
                continue  # Double slash //
            if constants.KEYS.ITEMS in schema:
                schema = schema[constants.KEYS.ITEMS]
            else:
                if k not in schema:
                    raise RuntimeError(f"Failed to find path in schema: {key_path}")
                schema = schema[k]
        return schema

    def _schema_default(self, schema):
        type_ = schema[constants.KEYS.TYPE]
        if constants.KEYS.DEFAULT in schema:
            return copy.deepcopy(schema[constants.KEYS.DEFAULT])
        if type_ == constants.TYPES.OBJECT:
            # Shouldn't get here
            return {}
        elif type_ == constants.TYPES.ARRAY:
            length = schema.get(constants.KEYS.ARRAY_LENGTH, 0)
            if length <= 0:
                return []
            # Ideally a default should be set...
            item_type = schema.get(constants.KEYS.ITEMS, {}).get(constants.KEYS.TYPE)
            if item_type is None:
                return [None] * length
            if item_type == constants.TYPES.STRING:
                return [""] * length
            if item_type == constants.TYPES.INT:
                return [0] * length
            if item_type == constants.TYPES.FLOAT:
                return [0.0] * length
            if item_type == constants.TYPES.BOOL:
                return [False] * length
        elif type_ == constants.TYPES.STRING:
            return ""
        elif type_ == constants.TYPES.INT:
            return 0
        elif type_ == constants.TYPES.FLOAT:
            return 0.0
        elif type_ == constants.TYPES.BOOL:
            return False
        else:  # Unknown type
            return None

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def tags(self) -> List[str]:
        return copy.copy(self._tags)

    @property
    def variants(self) -> List[str]:
        return copy.copy(self._variants)
