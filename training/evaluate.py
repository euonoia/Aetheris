"""Evaluation script to run YOLOv8 validation and save metrics to experiment folder."""
import argparse
import os
import json
from ultralytics import YOLO
from training.utils import load_yaml, ensure_dir


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--outdir", required=True)
    return p.parse_args()


def main():
    args = parse_args()
    ensure_dir(args.outdir)
    model = YOLO(args.weights)
    metrics = model.val(data=args.data)
    # ultralytics returns a dict-like object; serialize essential parts
    metrics_path = os.path.join(args.outdir, "metrics.json")
    with open(metrics_path, "w") as fh:
        json.dump(metrics.boxes.obj if hasattr(metrics, 'boxes') else dict(metrics), fh, indent=2, default=str)
    print(f"Saved metrics to {metrics_path}")


if __name__ == "__main__":
    main()
