**Phase 7B — ML engineering reorganization**

This document explains the new project layout and how to run training/evaluation without touching the FastAPI app.

Highlights
----------
- Training code moved to `training/`.
- Datasets versioned under `datasets/`.
- Models stored in `models/pretrained`, `models/custom`, `models/archive`.
- Experiments stored under `experiments/experiment_xxx`.
- Detector loads model path from `app.core.config.MODEL_PATH` allowing hot-swap.

Run training
------------

Install training deps and run with a YAML config:

```bash
pip install -r training/requirements.txt
python training/train.py --config training/configs/barangay178.yaml
```

Evaluate weights
---------------

```bash
python training/evaluate.py --weights experiments/experiment_001/weights/best.pt --data datasets/barangay178_v1/data.yaml --outdir experiments/experiment_001
```

Compare models
--------------

```bash
python training/compare_models.py --a models/pretrained/yolov8n.pt --b models/custom/barangay178_v1.pt --data datasets/barangay178_v1/data.yaml --out compare_report.json
```

Switch production model
-----------------------
To change the model the detector loads, either set the `MODEL_PATH` environment variable used by `app.core.config`, or place the desired checkpoint under `backend/yolov8n.pt` (fallback). Recommended: set `MODEL_PATH` to the desired `models/custom/*.pt` path.
