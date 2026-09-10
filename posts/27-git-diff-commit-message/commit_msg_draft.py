"""Commit message draft from git diff — https://automate-lab.tistory.com/27"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from automate_lab.commit_msg import main

if __name__ == "__main__":
    raise SystemExit(main())
