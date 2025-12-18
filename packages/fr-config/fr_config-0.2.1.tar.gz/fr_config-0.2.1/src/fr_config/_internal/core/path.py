# Copyright (C) 2024 Floating Rock Studio Ltd
from __future__ import annotations
import os
from pathlib import Path
from typing import Union, Optional, List
import pyjson5
from ..utils.typing import ensure_list
from ..utils.path import match_version
from ... import constants

# MARK: Config


def find_config(
    path: Union[Path, str],
    name: str,
    variant: Optional[str] = None,
    tags: Union[str, List[str]] = None,
) -> Union[Path, None]:
    """Given a path, Find the config if it exists

    Args:
        path(str,Path): file path to search
        name(str): config name to find
        variant(str,List[str]): variant to load, if this is a string or None, it will also load "default"
        tag(str,List[str]): tags to search for in sequential order, defaults to published,latest

    Returns:
        Path or None
    """

    variant_name = variant or constants.DEFAULT_VARIANT
    variant_dir = path / constants.FR_CONFIG_DIR / name / variant_name
    if not variant_dir.exists():
        return None

    return match_version(variant_dir, tags)


def find_configs(
    path: Union[Path, str],
    name: str,
    variant: Union[List[str], str] = None,
    tags: Union[str, List[str]] = None,
    cascade: bool = True,
) -> List[Path]:
    """Given a path, resolve the configs in reverse order by variant and tag

    Args:
        path(str,Path): file path to search
        name(str): config name to find
        variant(str,List[str]): variant(s) to load, if this is a string or None, it will also load "default"
        tag(str,List[str]): tags to search for in sequential order, defaults to published,latest
        cascade(bool): If False will stop at first config found, otherwise will search each section of the path

    Returns:
        List[Path]

    Raises:
        RuntimeError: If a parent is specified and does not exist
        RecursionError: If a parent is specified that was already a part of the resolve stack
    """
    variants = ensure_list(variant) if isinstance(variant, (list, tuple, set)) else [variant, constants.DEFAULT_VARIANT]
    # uniquify but retain order
    variants = list(dict.fromkeys(variants))

    tags = ensure_list(tags) if tags else constants.TAGS.DEFAULT
    path = Path(path)
    configs = []
    root_paths = [Path(p) for p in os.getenv(constants.ROOT_PATH_VAR, "").split(os.pathsep) if p]
    root_path_parents = [p.parent for p in root_paths]
    while path.parent != path and path not in root_path_parents:
        parent_folder = path / constants.FR_CONFIG_DIR / name
        path = path.parent
        if not parent_folder.exists():
            continue

        for variant_name in variants:
            if not variant_name:
                continue

            variant_dir = parent_folder / variant_name
            if not variant_dir.exists():
                continue

            file = match_version(variant_dir, tags)
            if not file:
                continue
            with file.open("r", encoding="utf-8") as f:
                data = pyjson5.load(f)
                parent = data.get("$parent")
                if parent:
                    os.chdir(path)
                    parent_path = Path(os.path.expandvars(parent)).resolve()
                    if not parent_path.exists():
                        raise RuntimeError(f"{parent_path} requested by {file} does not exist")
                    path = parent_path

            if file in configs:
                print("Loaded Configs: ")
                for each in configs:
                    if each == file:
                        print(f"  {each}  <--")
                    else:
                        print(f"  {each}")
                print(f"  {file}  <--")
                raise RecursionError("Configs reference themselves, check for recursion")
            configs.append(file)
            if not cascade:
                return configs

    return configs


# MARK: Schema


def find_schema_path(schema_name: str) -> Path:
    """Search for a schema on the FR_CONFIG_SCHEMA_PATH paths

    Args:
        schema_name(str): name of schema

    Returns:
        Path

    Raises:
        LookupError: If no schema was found
    """
    for path in os.getenv(constants.SCHEMA_PATH_VAR, "").split(os.pathsep):
        config_path = Path(path) / f"{schema_name}{constants.FR_SCHEMA_EXT}"
        if config_path.exists():
            return config_path

    raise LookupError(f"Failed to find {schema_name}{constants.FR_SCHEMA_EXT} on {constants.SCHEMA_PATH_VAR}")
