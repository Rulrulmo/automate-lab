"""Daily job template for Windows Task Scheduler.

Blog: https://automate-lab.tistory.com/24
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from automate_lab.scheduled import force_utf8, run_logged


def job() -> None:
    # Replace with real work, e.g. sort_downloads / inbox processing.
    print("daily job ok")


if __name__ == "__main__":
    force_utf8()
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    raise SystemExit(run_logged(job, log_dir=log_dir))
