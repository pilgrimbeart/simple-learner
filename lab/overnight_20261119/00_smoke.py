"""Preparation check only: no scientific task or new histories are run."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from overnight_20261119_support import self_check
print(json.dumps(dict(purpose='handoff helper smoke test only',checks=self_check()),indent=2))
