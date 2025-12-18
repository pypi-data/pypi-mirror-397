import pytest
import os
from pathlib import Path


def pytest_configure(config):
    # configurations go here
    resource_dir = Path(__file__).parent.parent / "resources"
    assert resource_dir.exists()

    project_dir = resource_dir / "configs" / "Projects"
    assert project_dir.exists()
    os.environ["FR_PROJECTS_DIR"] = str(project_dir)
    os.environ["FR_CONFIG_SCHEMA_PATH"] += ";" + str(resource_dir / "schema")
    from fr_common.constants import PATHS

    assert PATHS.PROJECTS == project_dir.as_posix()
