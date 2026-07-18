"""
Dataset Engineering Toolkit Entry Point

Usage:
    python -m dataset_tools
    or
    python main.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from ui.app import main

if __name__ == "__main__":
    main()