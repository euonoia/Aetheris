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

DEFAULT_CUSTOM_MODEL = CUSTOM_DIR / "barangay178_v1.pt"
DEFAULT_PRETRAINED = PRETRAINED_DIR / "yolov8n.pt"

# ---------------------------------------------------------------------
# Active Model
# ---------------------------------------------------------------------

# Allow overriding through an environment variable.
# If no environment variable is provided, use the custom model.
MODEL_PATH = Path(
    os.environ.get("MODEL_PATH", str(DEFAULT_CUSTOM_MODEL))
)

# If the custom model does not exist yet,
# automatically fall back to the pretrained model.
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