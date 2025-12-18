import tempfile
from pathlib import Path
import json
import os
from fr_config import ConfigLoader, ConfigWriter
from fr_common.structs import Context


def test_load_shot():
    config = ConfigLoader("packages", Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path())
    assert len(config.loaded_paths()) == 2
    assert config.path == Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path()
    assert config.tags == ["published", "latest"]
    assert config.variants == ["default"]

    assert config._schema == {
        "__version__": 1,
        "packages": {
            "cascade": "append",
            "items": {"type": "string", "compare": {"type": "string", "default": "^(?:[!~]*)([_a-zA-Z0-9]+)-?.*?"}},
            "type": "array",
            "unique": True,
        },
        "tools": {
            "cascade": "update",
            "items": {
                "type": "object",
                "command": {"type": "string"},
                "packages": {
                    "cascade": "append",
                    "items": {
                        "type": "string",
                        "compare": {"type": "string", "default": "^(?:[!~]*)([_a-zA-Z0-9]+)-?.*?"},
                    },
                    "type": "array",
                },
                "variables": {
                    "cascade": "update",
                    "items": {"type": "string", "separator": {"type": "string", "default": "%pathsep%"}},
                    "type": "object",
                },
            },
            "type": "object",
        },
        "variables": {
            "cascade": "update",
            "items": {"type": "string", "separator": {"type": "string", "default": "%pathsep%"}},
            "type": "object",
        },
    }

    assert config._data == {
        "variables": {
            "ENABLE_LEGACY_RENDER": "1",
            "PATH": "/path/to/root/thing;/path/to/shot/specific/thing",
            "PREPATH": "/path/to/shot/other/thing;/path/to/other/thing",
        },
        "packages": ["pyside-5.15.2", "python-3.10.2", "custom_package.0.0.1+"],
        "tools": {
            "maya": {
                "command": "maya.exe",
                "packages": ["maya-2023.4", "pymel-4", "python-3.9.7", "another_package.0.0.2+"],
                "variables": {
                    "MAYA_RENDER_SETUP_INCLUDE_ALL_LIGHTS": "1",
                    "MAYA_SCRIPT_PATH": "/path/to/mel/scripts;/path/to/shot/mel/scripts",
                },
            },
            "rv": {
                "command": "rv.exe",
                "packages": ["rv_local_install", "rv_fr_plugins"],
                "variables": {"SOME_RV_FLAG": "0"},
            },
        },
    }
    assert set(config.keys()) == {"variables", "packages", "tools"}
    assert set(config.key_paths()) == {
        "/variables",
        "/variables/ENABLE_LEGACY_RENDER",
        "/variables/PATH",
        "/variables/PREPATH",
        "/packages",
        "/tools",
        "/tools/rv",
        "/tools/rv/command",
        "/tools/rv/variables",
        "/tools/rv/variables/SOME_RV_FLAG",
        "/tools/rv/packages",
        "/tools/maya",
        "/tools/maya/command",
        "/tools/maya/variables",
        "/tools/maya/variables/MAYA_RENDER_SETUP_INCLUDE_ALL_LIGHTS",
        "/tools/maya/variables/MAYA_SCRIPT_PATH",
        "/tools/maya/packages",
    }


def test_set_value():
    config = ConfigWriter("packages", Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path())
    config.load()
    config.set_data("packages", config.get_data("packages") + ["package-1", "package2-1+"])
    assert config.get_data("packages") == [
        "python-3.10.2",
        "custom_package.0.0.1+",
        "package-1",
        "package2-1+",
    ]
    assert config._data["packages"] == [
        "python-3.10.2",
        "custom_package.0.0.1+",
        "package-1",
        "package2-1+",
    ]

    config.set_data("/tools/maya/variables/SOME_ENV_VAR", "1")
    script_path = config.get_data("/tools/maya/variables/MAYA_SCRIPT_PATH")
    script_path["value"] += ";/path/to/local/value"
    config.set_data(
        "/tools/maya/variables/MAYA_SCRIPT_PATH",
        script_path,
    )
    assert config.get_data("/tools/maya/variables/SOME_ENV_VAR") == "1"
    assert config.get_data("/tools/maya/variables/MAYA_SCRIPT_PATH") == script_path


def test_commit():
    config = ConfigWriter("packages", Context.from_path("/FRCONFIG/Shots/SEQ_001/0010").path())
    config.set_data("packages", ["package-1", "package2-1+"])

    config.set_data("/tools/maya/variables/SOME_ENV_VAR", "1")
    config.set_data("/tools/maya/variables/MAYA_SCRIPT_PATH", {"value": "/path/to/local/value", "cascade": "append"})

    out_dir = Path(tempfile.mkdtemp())
    result = config.commit("This is a message", publish=True, output_dir=out_dir)
    assert result == (out_dir / "packages" / "default" / "v1.fr_config")
    assert len(list(result.parent.iterdir())) == 2
    assert (result.parent / ".v1.published").exists()

    with result.open("r", encoding="UTF-8") as f:
        data = json.load(f)

    # Remove the timestamp
    del data["__info__"]["created"]
    assert data == {
        "__info__": {
            "version": 1,
            "name": "packages",
            "variant": "default",
            "author": os.getlogin(),
            "schema": config._schema_path.as_posix(),
            "source": None,
            "commit_message": "This is a message",
        },
        "packages": ["package-1", "package2-1+"],
        "tools": {
            "maya": {
                "variables": {
                    "SOME_ENV_VAR": "1",
                    "MAYA_SCRIPT_PATH": {"value": "/path/to/local/value", "cascade": "append"},
                }
            }
        },
    }
