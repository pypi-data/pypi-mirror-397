# Copyright (C) 2024 Floating Rock Studio Ltd
from __future__ import annotations
import typing
from pathlib import Path
from typing import Protocol, List, Union, Any


# Sentinel object to distinguish between no default provided vs None as default
_SENTINEL = object()


class IConfigBase(Protocol):
    """Base protocol for config operations with shared properties and functionality."""

    @property
    def name(self) -> str:
        """The config name."""
        ...

    @property
    def path(self) -> Path:
        """The path to the config."""
        ...

    @property
    def tags(self) -> List[str]:
        """Optional tags to load, defaults to published,latest, order is important."""
        ...

    @property
    def variants(self) -> List[str]:
        """variant(s) to use, defaults to constants.KEYS.DEFAULT."""
        ...


class IConfigLoader(IConfigBase, Protocol):
    """Protocol for config loaders.

    Initializes a config
    Args:
        name(str): Config name
        context(Context): Context or path to load configs from
        variants(str|List[str]): variant(s) to load, defaults to constants.KEYS.DEFAULT
        tags(List[str]): Optional tags to load, defaults to published,latest, order is important
        cascade(bool): Load configs in a hierarchical cascade with top level configs loading first
        continue_on_error(bool): If a config in the stack is not valid, this will allow to load the remaining valid
                                 configs. Use this only when failing to resolve the config causes more problems
    """

    def load(
        self,
        path: Union[str, Path],
        variant: Union[List[str], str, None] = None,
        tags: Union[str, List[str]] = None,
        cascade: bool = True,
        continue_on_error: bool = False,
    ) -> "IConfigLoader":
        """Load the config at the specified context
        Args:
            path(Union[str, Path]): Context or path to load configs from
            variant(str|List[str]): variant(s) to load, defaults to constants.DEFAULT_VARIANT
            tags(List[str]): Optional tags to load, defaults to published,latest, order is important
            cascade(bool): Load configs in a hierarchical cascade with top level configs loading first
            continue_on_error(bool): If a config in the stack is not valid, this will allow to load the remaining valid
                                    configs. Use this only when failing to resolve the config causes more problems

        Returns:
            self
        """
        ...

    def loaded_paths(self) -> List[Path]:
        """Return list of paths that were loaded."""
        ...

    def keys(self) -> List[str]:
        """Return list of top-level keys in the config data."""
        ...

    def key_paths(self) -> List[str]:
        """Return list of all key paths in the config data."""
        ...

    def value(self, key_path: str, default=_SENTINEL) -> Any:
        """Get the value at the specified key path."""
        ...


class IConfigWriter(IConfigBase, Protocol):
    """Protocol for config writers.

    Allows writing of config data
    Args:
        name(str): Config name
        path(str): path to write configs to
        variants(str|List[str]): variant(s) to write, defaults to constants.KEYS.DEFAULT
        tags(List[str]): Optional tags to load, defaults to published,latest, order is important
        cascade(bool): Load configs in a hierarchical cascade with top level configs loading first
        continue_on_error(bool): If a config in the stack is not valid, this will allow to load the remaining valid
                                 configs. Use this only when failing to resolve the config causes more problems
    """

    @property
    def variant(self) -> str:
        """The current variant being written to."""
        ...

    def load(self) -> bool:
        """Load existing config data for modification.

        Returns:
            bool: True if config was loaded successfully, False otherwise
        """
        ...

    def get_data(self, key_path: str = "/", modify: bool = True, default: Any = _SENTINEL) -> Any:
        """Get data at the specified key path.

        Args:
            key_path(str): The path to the data to retrieve
            modify(bool): Whether to return a modifiable reference or a copy
            default: Value to return if key is not found

        Returns:
            The data at the specified path or default if not found
        """
        # Note, we explicitly use get_data instead of value to avoid confusion between loader and writer
        ...

    def remove_key(self, key_path: str) -> bool:
        """Remove a key from the config data.

        Args:
            key_path(str): The path to the key to remove

        Returns:
            bool: True if the key was removed, False if it didn't exist
        """
        ...

    def set_data(self, key_path: str, value: Any) -> None:
        """Set data at the specified key path.

        Args:
            key_path(str): The path where to set the data
            value(Any): The value to set
        """
        ...

    def metadata(self) -> dict:
        """Return the metadata dictionary for the config."""
        ...

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
        ...
