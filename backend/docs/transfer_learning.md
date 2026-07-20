**Phase 7 — Transfer Learning & Domain Adaptation**

Overview
--------

This document explains how to fine-tune a pretrained YOLOv8 model so it performs well on Philippine traffic scenes (barangay roads, highways, terminals, market areas, etc.). The approach uses transfer learning — we start from `yolov8n.pt` and fine-tune on a custom dataset containing only vehicle classes.

Dataset
-------

- Structure: `dataset/` with `train/`, `valid/`, `test/` following YOLO format.
- Use YOLO annotation format (one .txt per image). Use Label Studio, CVAT, or Roboflow for annotation.
- Only annotate vehicle classes: `car, motorcycle, bus, truck, jeepney, tricycle, van`.
- Do NOT annotate pedestrians, traffic enforcers, bicycles, signs, buildings, trees — they remain unlabeled to provide contextual realism.

Why only vehicle classes?
- The monitoring system focuses on vehicle counts and tracking. Lumping pedestrians or other objects reduces detector capacity for the target classes.

Training script
---------------

- `backend/train.py` is a beginner-friendly script that:
  - Loads a pretrained YOLOv8 checkpoint
  - Fine-tunes on your dataset
  - Copies the best weights to `backend/models/best.pt`
  - Copies any generated plots into `backend/models/` for inspection

Example command
---------------

```bash
cd backend
python train.py --data dataset/data.yaml --pretrained yolov8n.pt --epochs 50 --imgsz 640 --batch 16
```

Key training parameters (what they mean)
--------------------------------------

- `epochs`: Number of passes through the dataset. More epochs let the model fit better but risk overfitting.
- `imgsz`: Input image size (pixels). Larger improves accuracy but increases memory and compute.
- `batch`: Batch size per GPU. Larger batches stabilize training but require more memory.
- `workers`: Data loader worker processes for faster I/O.
- `cache`: Dataset caching strategy; `ram` or `disk` speeds up epochs at the cost of memory/disk space.
- `optimizer`: Optimizer name (leave default to use Ultralytics' recommended optimizer).
- `lr`: Initial learning rate. Small values (~1e-3 to 1e-5 depending on optimizer) are common for fine-tuning.
- `patience`: Early stopping patience in epochs — prevents wasting compute if validation stops improving.
- `device`: GPU index or `cpu`.

Validation metrics (how to interpret)
-----------------------------------

- Precision: Of detections predicted as a class, the fraction that are correct. High precision means few false positives.
- Recall: Of ground-truth objects, the fraction the model detected. High recall means few false negatives.
- mAP50: Mean Average Precision at IoU=0.5. Good general measure; values closer to 1.0 are better.
- mAP50-95: Average mAP across IoU thresholds 0.5:0.95. Stricter; useful to measure localization quality.
- Confusion Matrix: Shows which classes are confused with which. Look for off-diagonal mass to find confusions (e.g., jeepney vs bus).
- Precision-Recall Curve: Shows trade-off between precision and recall across confidence thresholds.
- Loss Curves: Training/validation loss over epochs. Look for divergence (overfitting) or plateau (underfitting).

Good vs poor values
-------------------
- Good: precision and recall both high (>0.8) and mAP50 > 0.7 for a realistic dataset. For small/occluded classes, lower values may be expected.
- Poor: Low precision + high recall -> many false positives. Low recall -> misses many vehicles. Low mAP50-95 but decent mAP50 -> localization needs improvement.

Model export & integration
--------------------------

- After training, `backend/train.py` copies the best checkpoint to `backend/models/best.pt`.
- To use the new model in the existing app, replace the path used when constructing the YOLO object from `yolov8n.pt` to `models/best.pt`.
  - The existing code loads the model via `YOLO(MODEL_PATH)`. Place `best.pt` at `backend/models/best.pt` and update `MODEL_PATH` accordingly or replace the file that the code currently points to.
- Do NOT modify ByteTrack or tracking code. The tracker uses detections from YOLO in the same format; a fine-tuned detector is a drop-in replacement.

Best practices and common mistakes
---------------------------------

- Do NOT train from scratch; always start with a pretrained checkpoint.
- Ensure consistent class IDs and names between `data.yaml` and annotations.
- Avoid duplicating images across splits. Keep validation/test strictly separate.
- High-quality bounding boxes matter more than thousands of noisy labels.
- Include varied Philippine-specific conditions (wet roads, low-light CCTV, angles, occlusion).
- If class imbalance exists, consider augmentations or class-weighting, but test carefully.

Next steps
----------

- Prepare the dataset following `backend/dataset/data.yaml`.
- Install training deps: `pip install -r backend/requirements.txt`.
- Run `python backend/train.py --data backend/dataset/data.yaml` and monitor runs/train/phase7.
