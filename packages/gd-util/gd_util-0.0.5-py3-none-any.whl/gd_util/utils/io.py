import shutil
import json
from pathlib import Path

import yaml

__all__ = [
    "fPath",
    "dump_json",
    "load_json",
    "dump_yaml",
    "load_yaml",
    "clean_dir",
]


def fPath(filepath: str | Path, *path_parts: str, mkdir: bool = False) -> Path:
    full_path = Path(filepath).parent.joinpath(*path_parts)
    if mkdir:
        full_path.mkdir(exist_ok=True, parents=True)
    return full_path


def clean_dir(path: str | Path):
    if Path(path).exists():
        shutil.rmtree(str(path))


# ---------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------


def dump_json(filename: str | Path, data, **kwargs):
    kwargs.setdefault("indent", 4)
    with open(str(filename), "w") as f:
        json.dump(data, f, **kwargs)


def load_json(filename: str | Path, **kwargs):
    with open(str(filename), "r") as f:
        return json.load(f, **kwargs)


# ---------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------

def dump_yaml(filename: str | Path, data, **kwargs) -> None:
    """
    Dump data to YAML using PyYAML safe_dump.

    Defaults:
    - block style
    - human-readable
    """
    kwargs.setdefault("default_flow_style", False)
    kwargs.setdefault("sort_keys", False)

    with open(str(filename), "w") as f:
        yaml.safe_dump(data, f, **kwargs)


def load_yaml(filename: str | Path) -> dict:
    """
    Load YAML using PyYAML safe_load.
    """
    with open(str(filename), "r") as f:
        return yaml.safe_load(f)
