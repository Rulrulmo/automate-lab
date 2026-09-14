"""VLOOKUP-style join via pandas.merge — https://automate-lab.tistory.com/34"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from automate_lab.table_merge import main

if __name__ == "__main__":
    raise SystemExit(main())
