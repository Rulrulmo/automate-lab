"""Collect ERROR/CRITICAL log lines to CSV — https://automate-lab.tistory.com/41"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from automate_lab.log_errors import main

if __name__ == "__main__":
    raise SystemExit(main())
