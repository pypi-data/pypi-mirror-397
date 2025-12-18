from fr_config._internal.utils import path as fr_path
from fr_config import constants
from pathlib import Path
import tempfile


def test_unique_tag():
    d = Path(tempfile.mkdtemp())
    (d / "v1").mkdir()
    (d / "v2").mkdir()
    (d / "v3").mkdir()

    fr_path.set_tag(d / "v2", constants.TAGS.PUBLISHED)
    assert set([f.name for f in d.iterdir()]) == {"v1", "v2", "v3", ".v2.published"}
    fr_path.set_tag(d / "v3", constants.TAGS.PUBLISHED)
    assert set([f.name for f in d.iterdir()]) == {"v1", "v2", "v3", ".v3.published"}


def test_multi_tag():
    d = Path(tempfile.mkdtemp())
    (d / "v1").mkdir()
    (d / "v2").mkdir()
    (d / "v3").mkdir()

    fr_path.set_tag(d / "v2", constants.TAGS.DEPRECATED)
    assert set([f.name for f in d.iterdir()]) == {"v1", "v2", "v3", ".v2.deprecated"}
    fr_path.set_tag(d / "v3", constants.TAGS.DEPRECATED)
    assert set([f.name for f in d.iterdir()]) == {"v1", "v2", "v3", ".v2.deprecated", ".v3.deprecated"}


def test_remove_tag():
    d = Path(tempfile.mkdtemp())
    (d / "v1").mkdir()
    (d / "v2").mkdir()
    (d / "v3").mkdir()

    fr_path.set_tag(d / "v2", constants.TAGS.PUBLISHED)
    assert set([f.name for f in d.iterdir()]) == {"v1", "v2", "v3", ".v2.published"}
    fr_path.remove_tag(d / "v2", constants.TAGS.PUBLISHED)
    assert set([f.name for f in d.iterdir()]) == {"v1", "v2", "v3"}


def test_lock_tag():
    d = Path(tempfile.mkdtemp())
    (d / "v1").mkdir()
    (d / "v2").mkdir()
    (d / "v3").mkdir()
    with fr_path.LockVersion(d / "v4"):
        assert set([f.name for f in d.iterdir()]) == {"v1", "v2", "v3", ".v4.locked"}
    assert set([f.name for f in d.iterdir()]) == {"v1", "v2", "v3"}


def test_get_versions():
    d = Path(tempfile.mkdtemp())
    (d / "v1").mkdir()
    (d / "v2").mkdir()
    (d / "v3").mkdir()
    (d / "v4").mkdir()

    fr_path.set_tag(d / "v2", constants.TAGS.PUBLISHED)
    fr_path.set_tag(d / "v4", constants.TAGS.DEPRECATED)
    versions = fr_path.get_versions(d)
    assert versions == {
        "v1": {"number": 1, "name": "v1", "path": d / "v1", "tags": []},
        "v2": {"number": 2, "name": "v2", "path": d / "v2", "tags": [constants.TAGS.PUBLISHED]},
        "v3": {"number": 3, "name": "v3", "path": d / "v3", "tags": [constants.TAGS.LATEST]},
    }


def test_get_versions_files():
    d = Path(tempfile.mkdtemp())
    (d / "v1.ext").touch()
    (d / "v2.ext").touch()
    (d / "v3.ext").touch()
    (d / "v4.ext").touch()

    fr_path.set_tag(d / "v2.ext", constants.TAGS.PUBLISHED)
    fr_path.set_tag(d / "v4.ext", constants.TAGS.DEPRECATED)
    versions = fr_path.get_versions(d)
    assert versions == {
        "v1.ext": {"number": 1, "name": "v1.ext", "path": d / "v1.ext", "tags": []},
        "v2.ext": {"number": 2, "name": "v2.ext", "path": d / "v2.ext", "tags": [constants.TAGS.PUBLISHED]},
        "v3.ext": {"number": 3, "name": "v3.ext", "path": d / "v3.ext", "tags": [constants.TAGS.LATEST]},
    }


def test_get_version_tags():
    d = Path(tempfile.mkdtemp())
    (d / "v1").mkdir()
    (d / "v2").mkdir()
    (d / "v3").mkdir()
    (d / "v4").mkdir()

    fr_path.set_tag(d / "v2", constants.TAGS.PUBLISHED)
    fr_path.set_tag(d / "v4", constants.TAGS.DEPRECATED)
    tags = fr_path.get_version_tags(d)
    assert tags == {
        "v2": [constants.TAGS.PUBLISHED],
        "v4": [constants.TAGS.DEPRECATED],
    }


def test_get_version_tags_files():
    d = Path(tempfile.mkdtemp())
    (d / "v1.ext").touch()
    (d / "v2.ext").touch()
    (d / "v3.ext").touch()
    (d / "v4.ext").touch()

    fr_path.set_tag(d / "v2.ext", constants.TAGS.PUBLISHED)
    fr_path.set_tag(d / "v4.ext", constants.TAGS.DEPRECATED)
    tags = fr_path.get_version_tags(d)
    assert tags == {
        "v2": [constants.TAGS.PUBLISHED],
        "v4": [constants.TAGS.DEPRECATED],
    }


def test_get_next_version():
    d = Path(tempfile.mkdtemp())
    (d / "v1").mkdir()
    (d / "v2").mkdir()

    assert fr_path.get_next_version(d) == "v3"
    assert fr_path.get_next_version(d, format="v{:02d}") == "v03"
    assert fr_path.get_next_version(d, format="{0}") == "1"

    d = Path(tempfile.mkdtemp())
    (d / "1").mkdir()
    (d / "2").mkdir()
    assert fr_path.get_next_version(d) == "3"
    d = Path(tempfile.mkdtemp())
    assert fr_path.get_next_version(d) == "v1"
