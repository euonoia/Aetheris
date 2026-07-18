"""Top-level training launcher that reads a YAML config and runs training.

Usage:
  python training/train.py --config training/configs/barangay178.yaml
"""
import sys
import os

# Make sure the project root (parent of this "training" folder) is importable,
# so "from training.utils import ..." works no matter where this script is run from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from ultralytics import YOLO
from training.utils import load_yaml, ensure_dir, timestamp

import argparse
import os
from ultralytics import YOLO
from training.utils import load_yaml, ensure_dir, timestamp


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, help="Path to YAML config")
    return p.parse_args()


def main():
    args = parse_args()
    cfg = load_yaml(args.config)

    # Build run name
    run_name = cfg.get("experiment_name") or f"run_{timestamp()}"
    project = cfg.get("project", "../experiments")
    run_dir = os.path.join(project, run_name)
    ensure_dir(run_dir)

    pretrained = cfg.get("pretrained", "yolov8n.pt")

    model = YOLO(pretrained)

    train_kwargs = {
        "data": cfg["data"],
        "epochs": cfg.get("epochs", 50),
        "imgsz": cfg.get("imgsz", 640),
        "batch": cfg.get("batch", 16),
        "workers": cfg.get("workers", 4),
        "project": project,
        "name": run_name,
        "cache": cfg.get("cache", False),
    }

    if cfg.get("device"):
        train_kwargs["device"] = cfg.get("device")
    if cfg.get("optimizer"):
        train_kwargs["optimizer"] = cfg.get("optimizer")
    if cfg.get("learning_rate"):
        train_kwargs["lr0"] = cfg.get("learning_rate")

    print("Training with configuration:")
    for k, v in cfg.items():
        print(f"  {k}: {v}")

    model.train(**train_kwargs)

    # locate best weights and copy to models/custom with a versioned name
    weights_src = os.path.join(project, run_name, "weights", "best.pt")
    models_custom = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "custom")
    os.makedirs(models_custom, exist_ok=True)

    if os.path.exists(weights_src):
        dst_name = f"{cfg.get('dataset_version','dataset')}_{run_name}_best.pt"
        dst_path = os.path.join(models_custom, dst_name)
        import shutil

        shutil.copy2(weights_src, dst_path)
        print(f"Copied best weights to {dst_path}")
    else:
        print(f"Warning: best weights not found at {weights_src}")


if __name__ == "__main__":
    main()
