# Copyright (C) 2024 Floating Rock Studio Ltd
# This file has been copied from fr_common.path
from __future__ import annotations
import os
import re
from collections import defaultdict
import json
import datetime
from pathlib import Path
from typing import Union, List, Set, Dict, Any
import pyjson5
from .typing import ensure_list
from ... import constants


def _get_version_number(name: str):
    if match := constants.FILE_VERSION_REGEX.match(name):
        return int(match.group("number"))
    return -1


def match_version(
    parent_folder: Union[str, Path],
    tags: Union[None, str, List[str]] = None,
    hide_tags: Set[str] = None,
) -> Union[None, Path]:
    """Find a version in a folder matching the requested tags

    Args:
        parent_folder(str|Path): Path to folder to search
        tags(str,List[str]): tags to search for, defaults to published,latest, this searches in order
        hide_tags(Set[str]): Tags to ignore, defaults to {locked,deprecated}

    Returns:
        Path or None
    """
    parent_folder = Path(parent_folder)
    hide_tags = set(hide_tags) if hide_tags is not None else set(constants.TAGS.HIDE)
    tags = ensure_list(tags) if tags else constants.TAGS.DEFAULT
    hide_tags = hide_tags.difference(set(tags))
    config_tags = get_version_tags(parent_folder)
    ordered = sorted(config_tags, key=_get_version_number, reverse=True)
    # Search sequentially based on tag, not file order
    for tag in tags:
        for version in ordered:
            tag_names = config_tags[version]
            if hide_tags.intersection(tag_names):
                continue
            if tag in tag_names:
                path = parent_folder / version
                if path.exists():
                    # directory
                    return path
                try:
                    # TODO: What if multiple formats in this dir?
                    path = next(parent_folder.glob(version + ".*"))
                except StopIteration:
                    continue
                return path  # File
    if constants.TAGS.LATEST in tags:
        latest_number = 0
        latest_path = None
        for file in parent_folder.iterdir():
            if file.name.startswith("."):
                continue
            if match := constants.FILE_VERSION_REGEX.match(file.name):
                file_tags = config_tags.get(file.stem, [])
                if hide_tags.intersection(file_tags):
                    continue
                number = int(match.group("number"))
                if number > latest_number:
                    latest_number = number
                    latest_path = file
        if latest_path:
            return latest_path
    return None


def get_version_tags(parent_folder: Union[str, Path]) -> Dict[str, List[str]]:
    """Get the version tags in a folder
    This does not include the latest tag

    Args:
        parent_folder(str|Path): Path to folder to search

    Returns:
        Dict[str,List[str]]

    """
    parent_folder = Path(parent_folder)
    tags = defaultdict(list)
    for file in parent_folder.iterdir():
        if not file.is_file():
            continue
        if match := constants.TAG_REGEX.match(file.name):
            tags[match.group("version")].append(match.group("tag"))
    return dict(tags)


def get_versions(parent_folder: Union[str, Path], hide_tags: Set[str] = None) -> List[Dict[str, Any]]:
    """Get the versions in a folder with their corresponding tags

    Args:
        parent_folder(str|Path): Path to folder to search
        hide_tags(Set[str]): Tags to ignore, defaults to {locked,deprecated}

    Returns:
        Dict[str,Any]

    """
    parent_folder = Path(parent_folder)
    hide_tags = set(hide_tags) if hide_tags is not None else set(constants.TAGS.HIDE)
    contents = list(parent_folder.iterdir())
    folder_tags = get_version_tags(parent_folder)

    latest = 0
    latest_data = None
    file_data = {}
    for file in contents:
        if file.name.startswith("."):
            continue
        if match := constants.FILE_VERSION_REGEX.match(file.name):
            file_tags = folder_tags.get(file.stem, [])
            if hide_tags.intersection(file_tags):
                continue
            latest = max(latest, int(match.group("number")))
            data = {
                "number": int(match.group("number")),
                "name": file.name,
                "path": file,
                "tags": file_tags,
            }
            file_data[file.name] = data
            if latest == data["number"]:
                latest_data = data

    if latest_data:
        latest_data["tags"].append(constants.TAGS.LATEST)

    return file_data


def set_tag(path: Union[str, Path], tag):
    """Adds a tag to a path, if this tag is unique it will remove from other files in the folder

    Args:
        path(str): Path to tag
        tag(str): tag to set
    """
    path = Path(path)
    tag_file = (path.parent) / f".{path.stem}.{tag}"
    if tag_file.exists():
        return
    if tag in constants.TAGS.UNIQUE:
        for file in path.parent.iterdir():
            if match := constants.TAG_REGEX.match(file.name):
                if tag == match.group("tag"):
                    file.unlink()

    tag_file.touch()
    with tag_file.open("w", encoding="utf-8") as f:
        data = {
            "user": os.getlogin(),
            "date": datetime.datetime.now().isoformat(),
        }
        json.dump(data, f, indent=2)


def remove_tag(path: Union[str, Path], tag):
    """Removes a tag from a path

    Args:
        path(str): Path to untag
        tag(str): tag to remove
    """
    path = Path(path)
    tag_file = (path.parent) / f".{path.stem}.{tag}"
    tag_file.unlink(missing_ok=True)


def get_next_version(parent_folder: Union[str, Path], format: str = None):
    """Get the next version in the folder, this includes any deprecated versions

    Args:
        parent_folder(Path)
        format(str): optional format string, takes one arg for version int
    """
    parent_folder = Path(parent_folder)
    contents = list(parent_folder.iterdir())
    expr = constants.FILE_VERSION_REGEX
    if format:
        # Replace standard format with expression
        expr = re.compile(re.sub(r"\{.*\}", "(?P<number>[0-9+])", format))
    latest = 0
    file: Path = None
    for file in contents:
        if file.name.startswith("."):
            continue
        if match := expr.match(file.name):
            latest = max(latest, int(match.group("number")))
            if not format:
                start = file.name[: match.start("number")]
                end = file.name[match.end("number") :]
                format = f"{start}{{:0{len(match.group('number'))}}}{end}"

    if format:
        return format.format(latest + 1)

    if latest == 0:
        return "v1"

    # Unlikely to get here unless regex misses a file
    if file.name.startswith("v"):
        return f"v{latest+1}"
    return str(latest + 1)


class LockVersion:
    """Creates a .name.locked file to be used while writing.

    Args:
        path(str): Path to lock, must be named v123 or 123 to use with tagging
        force(bool): If True will not error if the path is already locked
    """

    def __init__(self, path: Union[str, Path], force: bool = False):
        self._path: Path = Path(path)
        self._lock: Path = self._path.parent / f".{self._path.stem}.{constants.TAGS.LOCKED}"
        if not force and self._lock.exists():
            raise RuntimeError(f"Lock file already exists: {self._lock}")

    def __enter__(self) -> LockVersion:
        self._lock.touch()
        with self._lock.open("w", encoding="utf-8") as f:
            data = {
                "user": os.getlogin(),
                "date": datetime.datetime.now().isoformat(),
            }
            json.dump(data, f, indent=2)
        return self

    def __exit__(self, *args):
        self._lock.unlink(missing_ok=True)
