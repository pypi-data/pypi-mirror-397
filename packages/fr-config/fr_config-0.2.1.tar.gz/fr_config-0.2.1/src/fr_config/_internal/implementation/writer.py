# Copyright (C) 2024 Floating Rock Studio Ltd
from __future__ import annotations
import typing
import copy
from pathlib import Path
import json
import os
import datetime
import pyjson5
from .base import ConfigBase
from ..utils import path as path_utils
from ..core.path import find_config
from ..utils.logging import get_logger
from ..core import validate
from ... import constants
from ...interfaces import IConfigWriter

_LOG = get_logger("fr_config")


class ConfigWriter(ConfigBase, IConfigWriter):
    """Allows writing of config data
    Args:
        name(str): Config name
        path(str): path to write configs to
        variants(str|List[str]): variant(s) to write, defaults to constants.KEYS.DEFAULT
        tags(List[str]): Optional tags to load, defaults to published,latest, order is important
        cascsade(bool): Load configs in a hierarchical cascade with top level configs loading first
        continue_on_error(bool): If a config in the stack is not valid, this will allow to load the remaining valid
                                 configs. Use this only when failing to resolve the config causes more propblems
    """

    def __init__(
        self,
        name: str,
        path: typing.Union[str, Path],
        variant: typing.Union[str, None] = None,
        tags: typing.Union[str, typing.List[str]] = None,
    ):
        super().__init__(name=name, path=path, variant=variant, tags=tags)
        self._current_path = find_config(self.path, self.name, self.variant, tags=tags)
        self._data = {}
        self._loaded = False

    @property
    def variant(self) -> str:
        return self.variants[0] if self.variants else constants.DEFAULT_VARIANT

    def load(self) -> bool:
        if not self._current_path:
            return False

        try:
            with self._current_path.open("r", encoding="UTF-8") as f:
                self._data = pyjson5.load(f)
        except pyjson5.Json5Exception as e:
            raise IOError("Failed to parse config %s", self._current_path.as_posix()) from e
        self._loaded = True
        return True

    _SENTINEL = object()

    def get_data(self, key_path: str = "/", modify: bool = True, default=_SENTINEL):
        schema = self._schema
        data = self._data if modify else copy.deepcopy(self._data)
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
        last_key = keys[-1]
        item_schema = schema.get(constants.KEYS.ITEMS, {})
        item_type = schema.get(constants.KEYS.TYPE)

        if item_type in (None, constants.TYPES.OBJECT) and item_schema:
            schema = item_schema.get(last_key, item_schema)
        else:
            schema = item_schema or schema.get(last_key, {})
        if not schema:
            if default is not self._SENTINEL:
                return default
            raise RuntimeError(f"Failed to find path in schema: {key_path}")

        if not last_key in data:
            data[last_key] = self._schema_default(schema)

        return data[last_key]

    def remove_key(self, key_path: str) -> bool:
        data = self._data
        keys = key_path.strip("/").split("/")
        for k in keys[0:-1]:
            if not k:
                continue  # Double slash //
            if constants.KEYS.ITEMS in schema:
                schema = schema[constants.KEYS.ITEMS]
            else:
                if k not in schema:
                    raise RuntimeError(f"Failed to find path in schema: {key_path}")
                schema = schema[k]

            if k not in data:
                return False
            data = data[k]
        last_key = keys[-1]
        if not last_key in data:
            return False
        del data[last_key]
        return True

    def set_data(self, key_path, value):
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
                    raise RuntimeError(f"Failed to find path in schema: {key_path}")
                schema = schema[k]

            if k not in data:
                # Set default if dictionary
                type_ = schema[constants.KEYS.TYPE]
                if type_ == constants.TYPES.OBJECT:
                    data[k] = {}
            data = data[k]
        last_key = keys[-1]
        # TODO: This validation fails for new object keys (items)
        # schema = schema[last_key]
        # item_schema = schema.get(KEYS.ITEMS, {})
        # try:
        #     _validate.validate({last_key: value}, schema, name=key_path)
        # except _validate.DataValidationException as e:
        #     _LOG.exception("Cannot save, Failed to validate data")
        #     raise e

        data[last_key] = value

    def metadata(self):
        return self._data.get(constants.KEYS.METADATA, {})

    def commit(self, message: str, publish: bool = False, output_dir: typing.Optional[Path] = None) -> Path:
        """Write a new file and optionally publish it

        Args:
            message(str): Commit message, this is saved in the file
            publish(bool): If specified will tag this file as published
            output_dir(Path): Optional override for directory to save to
                              Use with caution, setting this will skip some validations
                              The result output will be output_dir / configName / variant

        Returns:
            Path: path to saved config file
        """
        # validate the data

        try:
            # validate against the fr_schema
            validate.validate(self._data, self._schema, name=self.name)
        except validate.DataValidationException as e:
            _LOG.exception("Cannot save, Failed to validate data")
            raise e

        variant = self._variants[0]
        if output_dir:
            output_dir = Path(output_dir)
        else:
            output_dir = self.path / constants.FR_CONFIG_EXT
        target_dir: Path = output_dir / self.name / variant
        target_dir.mkdir(parents=True, exist_ok=True)

        # Get next version
        version = path_utils.get_next_version(target_dir, format="v{}" + constants.FR_CONFIG_EXT)
        out_file = target_dir / version
        with path_utils.LockVersion(out_file):
            # Get output dict
            out_data = copy.deepcopy(self._data)
            out_data[constants.KEYS.METADATA] = {
                "source": self._current_path.as_posix() if (self._loaded and self._current_path) else None,
                "version": int(version.strip("v").split(".")[0]),
                "name": self.name,
                "variant": variant,
                "schema": self._schema_path.as_posix(),
                "author": os.getlogin(),
                "created": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                "commit_message": str(message),
            }

            with out_file.open("w", encoding="UTF-8") as f:
                f.write(json.dumps(out_data, indent=4))

        if publish:
            path_utils.set_tag(out_file, constants.TAGS.PUBLISHED)
        return out_file
