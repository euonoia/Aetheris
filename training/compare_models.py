"""Compare two YOLO model checkpoints on metrics and model properties.

Produces a small report containing precision/recall/mAP, model size, and a simple timing.
"""
import argparse
import os
import time
import json
from ultralytics import YOLO


def model_size(path):
    return os.path.getsize(path)


def time_inference(path, device=0, runs=10):
    model = YOLO(path)
    # warmup
    model.predict(source=[[0]*3]*1, device=device)
    start = time.time()
    for _ in range(runs):
        model.predict(source=[[0]*3]*1, device=device)
    elapsed = time.time() - start
    return elapsed / runs


def val_metrics(path, data):
    model = YOLO(path)
    metrics = model.val(data=data)
    return metrics


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--out", default="compare_report.json")
    return p.parse_args()


def main():
    args = parse_args()
    report = {}
    for key in ["a", "b"]:
        path = getattr(args, key)
        report[path] = {}
        report[path]["size_bytes"] = model_size(path)
        report[path]["avg_infer_s"] = time_inference(path)
        metrics = val_metrics(path, args.data)
        report[path]["metrics"] = str(metrics)

    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=2)

    print(f"Saved comparison report to {args.out}")


if __name__ == "__main__":
    main()
