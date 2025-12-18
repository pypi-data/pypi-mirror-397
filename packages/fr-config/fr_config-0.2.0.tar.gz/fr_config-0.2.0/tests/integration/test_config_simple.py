import tempfile
import pytest
from pathlib import Path
import json
import os
from fr_config import ConfigLoader, ConfigWriter
from fr_config.exceptions import DataValidationException
from fr_common.structs import Context


def test_load_reparent():
    config = ConfigLoader("simple", Context.from_path("/FRCONFIG/Shots/SEQ_001/0020").path())
    assert len(config.loaded_paths()) == 2
    assert config.path == Context.from_path("/FRCONFIG/Shots/SEQ_001/0020").path()
    assert config.tags == ["published", "latest"]
    assert config.variants == ["default"]
    expected = [
        (Path(os.getenv("FR_PROJECTS_DIR")) / "../reparent/.fr_config/simple/default/v1.fr_config").resolve(),
        Path(os.getenv("FR_PROJECTS_DIR"))
        / "FR0001_FRCONFIG/03_Production/Shots/SEQ_001/0020/.fr_config/simple/default/v1.fr_config",
    ]
    assert config.loaded_paths() == expected
    assert config._data == {
        "custom_mode": False,
        "default_shelf": "FR_default",
        "fps": 24.0,
        "playblast_settings": {"frame_step": 2, "overscan": 1.5},
        "publish_defaults": {"handles": [10, 10], "publish_type": "AnimFinal"},
        "resolution": [512, 512],
        "tools": ["restricted_tool_1", "restricted_tool2"],
    }
    assert set(config.keys()) == {
        "custom_mode",
        "default_shelf",
        "fps",
        "playblast_settings",
        "publish_defaults",
        "resolution",
        "tools",
    }

    assert set(config.key_paths()) == {
        "/custom_mode",
        "/default_shelf",
        "/fps",
        "/playblast_settings",
        "/playblast_settings/frame_step",
        "/playblast_settings/overscan",
        "/publish_defaults",
        "/publish_defaults/handles",
        "/publish_defaults/publish_type",
        "/resolution",
        "/tools",
    }


def test_load_shot():
    config = ConfigLoader("simple", Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path())
    assert len(config.loaded_paths()) == 3
    assert config.path == Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path()
    assert config.tags == ["published", "latest"]
    assert config.variants == ["default"]
    assert config._data == {
        "custom_mode": False,
        "default_shelf": "FR_default",
        "fps": 30.0,
        "playblast_settings": {"frame_step": 2, "overscan": 1.5},
        "publish_defaults": {"handles": [10, 10], "publish_type": "AnimFinal"},
        "resolution": [2048, 1120],
        "tools": ["restricted_tool_1", "restricted_tool2", "restricted_tool3"],
    }
    assert set(config.keys()) == {
        "custom_mode",
        "default_shelf",
        "fps",
        "playblast_settings",
        "publish_defaults",
        "resolution",
        "tools",
    }

    assert set(config.key_paths()) == {
        "/custom_mode",
        "/default_shelf",
        "/fps",
        "/playblast_settings",
        "/playblast_settings/frame_step",
        "/playblast_settings/overscan",
        "/publish_defaults",
        "/publish_defaults/handles",
        "/publish_defaults/publish_type",
        "/resolution",
        "/tools",
    }


def test_set_value():
    config = ConfigWriter("simple", Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path())
    config.load()
    config.set_data("fps", 18.0)
    assert config.get_data("fps") == 18.0
    assert config._data["fps"] == 18.0

    config.set_data("/publish_defaults/publish_type", "Environment")
    assert config.get_data("publish_defaults") == {"publish_type": "Environment", "handles": [10, 10]}


def test_commit():
    config = ConfigWriter("simple", Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path())
    config.set_data("fps", 18.0)
    config.set_data("/publish_defaults/publish_type", "Environment")

    out_dir = Path(tempfile.mkdtemp())
    result = config.commit("This is a message", publish=True, output_dir=out_dir)
    assert result == (out_dir / "simple" / "default" / "v1.fr_config")
    assert len(list(result.parent.iterdir())) == 2
    assert (result.parent / ".v1.published").exists()

    with result.open("r", encoding="UTF-8") as f:
        data = json.load(f)

    # Remove the timestamp
    del data["__info__"]["created"]
    assert data == {
        "__info__": {
            "source": None,
            "version": 1,
            "name": "simple",
            "variant": "default",
            "author": os.getlogin(),
            "commit_message": "This is a message",
            "schema": config._schema_path.as_posix(),
        },
        "fps": 18.0,
        "publish_defaults": {
            "publish_type": "Environment",
        },
    }


def test_load_broken():
    with pytest.raises(DataValidationException):
        ConfigLoader("simple", Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path(), variant="broken")
