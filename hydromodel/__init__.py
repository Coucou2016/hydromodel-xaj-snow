"""
Author: Wenyu Ouyang
Date: 2024-02-09 15:56:48
LastEditTime: 2025-10-30 21:45:00
LastEditors: Wenyu Ouyang
Description: Top-level package for hydromodel with unified interfaces
FilePath: \\hydromodel\\hydromodel\\__init__.py
Copyright (c) 2023-2024 Wenyu Ouyang. All rights reserved.
"""

import os
from pathlib import Path
from hydroutils import hydro_file
import yaml
import re

# Import unified interfaces for easy access
try:
    from .trainers.unified_calibrate import calibrate
    from .trainers.unified_simulate import UnifiedSimulator
    from .trainers.basin import Basin

    # Import unit conversion functions from hydroutils
    from hydroutils.hydro_units import (
        mm_per_time_to_m3_per_s,
        m3_per_s_to_mm_per_time,
        detect_time_interval,
        get_time_interval_info,
        validate_unit_compatibility,
    )

    __all__ = [
        "calibrate",
        "UnifiedSimulator",
        "Basin",
        "SETTING",
        "CACHE_DIR",
        "mm_per_time_to_m3_per_s",
        "m3_per_s_to_mm_per_time",
        "detect_time_interval",
        "get_time_interval_info",
        "validate_unit_compatibility",
    ]
except ImportError:
    # Fallback if unified interfaces are not available
    __all__ = ["SETTING", "CACHE_DIR"]

__author__ = """Wenyu Ouyang"""
__email__ = "wenyuouyang@outlook.com"
__version__ = "0.3.0"


CACHE_DIR = hydro_file.get_cache_dir()


def _find_setting_file() -> str | None:
    """Find hydro_setting.yml with portable-friendly precedence.

    Precedence:
    1) Env var HYDRO_SETTING_FILE / HYDROMODEL_SETTING_FILE
    2) Repo root (one level above this package) : ./hydro_setting.yml
    3) Current working directory : ./hydro_setting.yml
    4) User home directory : ~/hydro_setting.yml (legacy default)
    """
    env_path = os.environ.get("HYDRO_SETTING_FILE") or os.environ.get(
        "HYDROMODEL_SETTING_FILE"
    )
    candidates: list[str] = []
    if env_path:
        candidates.append(env_path)

    repo_root = Path(__file__).resolve().parents[1]
    candidates.extend(
        [
            str(repo_root / "hydro_setting.yml"),
            str(Path.cwd() / "hydro_setting.yml"),
            str(Path.home() / "hydro_setting.yml"),
        ]
    )

    for p in candidates:
        try:
            if p and os.path.exists(p):
                return p
        except Exception:
            continue
    return None


SETTING_FILE = _find_setting_file() or os.path.join(Path.home(), "hydro_setting.yml")


def read_setting(setting_path):
    if not os.path.exists(setting_path):
        raise FileNotFoundError(f"Configuration file not found: {setting_path}")

    with open(setting_path, "r") as file:
        setting = yaml.safe_load(file)

    example_setting = (
        "local_data_path:\n"
        "  root: 'D:\\data\\waterism' # Update with your root data directory\n"
        "  datasets-origin: 'D:\\data\\waterism\\datasets-origin' # datasets-origin is the directory you put downloaded datasets\n"
        "  datasets-interim: 'D:\\data\\waterism\\datasets-interim' # the other choice for the directory you put downloaded datasets\n"
        "  basins-origin: 'D:\\data\\waterism\\basins-origin' # the directory put your own data\n"
        "  basins-interim: 'D:\\data\\waterism\\basins-interim' # the other choice for your own data"
    )

    if setting is None:
        raise ValueError(
            f"Configuration file is empty or has invalid format.\n\nExample configuration:\n{example_setting}"
        )

    # Define the expected structure
    expected_structure = {
        "local_data_path": [
            "root",
            "datasets-origin",
            "datasets-interim",
            "basins-origin",
            "basins-interim",
        ],
    }

    # Validate the structure
    try:
        for key, subkeys in expected_structure.items():
            if key not in setting:
                raise KeyError(f"Missing required key in config: {key}")

            if isinstance(subkeys, list):
                for subkey in subkeys:
                    if subkey not in setting[key]:
                        raise KeyError(
                            f"Missing required subkey '{subkey}' in '{key}'"
                        )
    except KeyError as e:
        raise ValueError(
            f"Incorrect configuration format: {e}\n\nExample configuration:\n{example_setting}"
        ) from e

    # Resolve relative local paths relative to the setting file directory
    base_dir = Path(setting_path).resolve().parent
    local_data_path = setting.get("local_data_path", {})
    for k, v in list(local_data_path.items()):
        if not isinstance(v, str) or not v.strip():
            continue
        v_str = v.strip()
        # Skip absolute paths and URLs like s3://
        if os.path.isabs(v_str) or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", v_str):
            continue
        local_data_path[k] = str((base_dir / v_str).resolve())
    setting["local_data_path"] = local_data_path

    return setting


try:
    SETTING = read_setting(SETTING_FILE)
except FileNotFoundError:
    # No setting file found: fall back to defaults without treating it as an error.
    default_root = os.path.join(Path.home(), "hydromodel_data")
    SETTING = {
        "local_data_path": {
            "root": default_root,
            "datasets-origin": os.path.join(default_root, "datasets-origin"),
            "datasets-interim": os.path.join(default_root, "datasets-interim"),
            "basins-origin": os.path.join(default_root, "basins-origin"),
            "basins-interim": os.path.join(default_root, "basins-interim"),
        }
    }
except ValueError as e:
    print(f"Warning: {e}")
    # Set default values when hydro_setting.yml is not found or invalid
    print(
        f"Using default data paths in home directory: {Path.home()}/hydromodel_data"
    )
    SETTING = None
    # Create default setting structure
    default_root = os.path.join(Path.home(), "hydromodel_data")
    SETTING = {
        "local_data_path": {
            "root": default_root,
            "datasets-origin": os.path.join(default_root, "datasets-origin"),
            "datasets-interim": os.path.join(default_root, "datasets-interim"),
            "basins-origin": os.path.join(default_root, "basins-origin"),
            "basins-interim": os.path.join(default_root, "basins-interim"),
        }
    }
except Exception as e:
    print(f"Unexpected error: {e}")
    # Set default values for unexpected errors
    print(
        f"Using default data paths in home directory: {Path.home()}/hydromodel_data"
    )
    SETTING = None
    default_root = os.path.join(Path.home(), "hydromodel_data")
    SETTING = {
        "local_data_path": {
            "root": default_root,
            "datasets-origin": os.path.join(default_root, "datasets-origin"),
            "datasets-interim": os.path.join(default_root, "datasets-interim"),
            "basins-origin": os.path.join(default_root, "basins-origin"),
            "basins-interim": os.path.join(default_root, "basins-interim"),
        }
    }
