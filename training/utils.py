"""Utility helpers for training workflows."""
import os
import time
import json
from pathlib import Path


def load_yaml(path):
    import yaml

    with open(path, "r") as f:
        return yaml.safe_load(f)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def save_metrics(dest: str, metrics: dict):
    ensure_dir(os.path.dirname(dest))
    with open(dest, "w") as fh:
        json.dump(metrics, fh, indent=2)


def timestamp():
    return time.strftime("%Y%m%d_%H%M%S")
