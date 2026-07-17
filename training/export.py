"""Export utilities: save/copy best model to models/custom and optionally export ONNX.
"""
import argparse
import os
import shutil


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True, help="Source best.pt path")
    p.add_argument("--name", required=True, help="Descriptive name for model file")
    return p.parse_args()


def main():
    args = parse_args()
    models_custom = os.path.join(os.getcwd(), "models", "custom")
    os.makedirs(models_custom, exist_ok=True)
    dst = os.path.join(models_custom, args.name)
    shutil.copy2(args.src, dst)
    print(f"Copied {args.src} -> {dst}")


if __name__ == "__main__":
    main()
