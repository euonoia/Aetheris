"""Simple inference helper for quick experiments.

Usage:
  python training/infer.py --weights models/custom/name.pt --image samples/img.jpg
"""
import argparse
from ultralytics import YOLO


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--image", required=True)
    return p.parse_args()


def main():
    args = parse_args()
    model = YOLO(args.weights)
    res = model(args.image)
    res.save()
    print("Saved inference outputs to the current folder.")


if __name__ == "__main__":
    main()
