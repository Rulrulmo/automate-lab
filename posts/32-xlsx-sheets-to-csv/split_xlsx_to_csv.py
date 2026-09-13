"""Split xlsx sheets to CSV — https://automate-lab.tistory.com/32"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from automate_lab.xlsx_split import main

if __name__ == "__main__":
    raise SystemExit(main())
