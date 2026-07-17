Models registry
===============

Structure
---------

models/
  pretrained/        # do NOT overwrite original pretrained checkpoints
    yolov8n.pt
  custom/            # trained models from experiments (never overwrite)
    barangay178_v1.pt
    barangay178_v2.pt
  archive/           # older or archived checkpoints

Each model file should be accompanied by a small README entry (or a central README) that records:
- Production model
- Training date
- Dataset version
- Precision / Recall / mAP50 / mAP50-95
- Notes
- Status (Production / Experimental)

Do not overwrite files in `pretrained/`. Save every successful custom model with a unique, versioned filename.
