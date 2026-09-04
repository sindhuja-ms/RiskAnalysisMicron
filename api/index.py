import sys
from pathlib import Path

# Ensure root directory is in python path for data loaders and engine
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from main import app