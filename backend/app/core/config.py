import os
from pathlib import Path

# ---------------------------------------------------------------------
# Base Project Directories
# ---------------------------------------------------------------------

# backend/app/core/config.py
# parents[2] resolves to the backend/ directory.
BASE_DIR = Path(__file__).resolve().parents[2]

APP_DIR = BASE_DIR / "app"

UPLOAD_DIR = APP_DIR / "uploads"
OUTPUT_DIR = APP_DIR / "outputs"

# ---------------------------------------------------------------------
# Model Directories
# ---------------------------------------------------------------------

MODELS_DIR = BASE_DIR / "models"

PRETRAINED_DIR = MODELS_DIR / "pretrained"
CUSTOM_DIR = MODELS_DIR / "custom"

DEFAULT_PRETRAINED = PRETRAINED_DIR / "yolov8n.pt"


def find_latest_custom_model() -> Path | None:
    """
    Look inside CUSTOM_DIR for any trained weights file ending in
    "best.pt" (train.py saves these with names like
    "barangay178_v1_experiment_001_best.pt", not plain "best.pt").
    Returns the most recently modified match, or None if none exist.
    """
    if not CUSTOM_DIR.exists():
        return None
    candidates = list(CUSTOM_DIR.glob("*best.pt"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


DEFAULT_CUSTOM_MODEL = find_latest_custom_model()

# ---------------------------------------------------------------------
# Active Model
# ---------------------------------------------------------------------

# Allow overriding through an environment variable.
# If no environment variable is provided, use the most recently
# trained custom model, if one exists.
_env_model_path = os.environ.get("MODEL_PATH")

if _env_model_path:
    MODEL_PATH = Path(_env_model_path)
elif DEFAULT_CUSTOM_MODEL is not None:
    MODEL_PATH = DEFAULT_CUSTOM_MODEL
else:
    MODEL_PATH = DEFAULT_PRETRAINED

# If whatever we picked doesn't actually exist on disk,
# fall back to the pretrained model as a last resort.
if not MODEL_PATH.exists():
    MODEL_PATH = DEFAULT_PRETRAINED

# ---------------------------------------------------------------------
# Directory Creation
# ---------------------------------------------------------------------

def ensure_dirs() -> None:
    """Create runtime directories if they do not already exist."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ensure_model_dirs() -> None:
    """Create model directories if they do not already exist."""
    PRETRAINED_DIR.mkdir(parents=True, exist_ok=True)
    CUSTOM_DIR.mkdir(parents=True, exist_ok=True)