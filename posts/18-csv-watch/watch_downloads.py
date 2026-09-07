"""Companion script for https://automate-lab.tistory.com/18

Prefer: python -m automate_lab.watch
This file mirrors the blog example for copy-paste from the posts/ path.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from automate_lab.watch import main

if __name__ == "__main__":
    main()
