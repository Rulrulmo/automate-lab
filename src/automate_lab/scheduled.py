"""Helpers for Windows Task Scheduler jobs: UTF-8 + file logging.

Blog: https://automate-lab.tistory.com/24
"""
from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable


def force_utf8() -> None:
    os.environ.setdefault("PYTHONUTF8", "1")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_logged(fn: Callable[[], None], *, log_dir: Path) -> int:
    """Run fn; append ok/error logs. Return 0 on success, 1 on failure."""
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        fn()
        with (log_dir / "ok.log").open("a", encoding="utf-8") as f:
            f.write(f"{stamp} ok\n")
        return 0
    except Exception:
        with (log_dir / "error.log").open("a", encoding="utf-8") as f:
            f.write(f"{stamp}\n{traceback.format_exc()}\n")
        return 1
