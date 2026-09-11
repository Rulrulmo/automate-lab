"""Watch an inbox for new CSV files; process after size stabilizes.

Blog: https://automate-lab.tistory.com/28
Related earlier sketch: automate_lab.watch (/18)
"""
from __future__ import annotations

import os
import time
from pathlib import Path

SKIP_SUFFIX = {".crdownload", ".tmp", ".part", ".download"}
POLL = 0.4


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    return Path(raw).expanduser() if raw else default


def wait_until_stable(path: Path, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    last = -1
    while time.monotonic() < deadline:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        if size == last and size > 0:
            return True
        last = size
        time.sleep(POLL)
    return False


def process_csv(path: Path, *, done: Path, dry_run: bool) -> None:
    """Default: optional pandas schema check, then move to DONE."""
    try:
        import pandas as pd

        df = pd.read_csv(path)
        cols = {c.lower() for c in df.columns}
        required = {"date", "amount"}
        missing = required - cols
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        nrows = len(df)
    except ImportError:
        import csv

        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        nrows = max(0, len(rows) - 1)

    done.mkdir(parents=True, exist_ok=True)
    dest = done / path.name
    if dry_run:
        print(f"DRY would move {path} -> {dest} rows={nrows}")
        return
    path.replace(dest)
    print(f"OK {dest} rows={nrows}")


def main() -> int:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as exc:
        raise SystemExit(
            "watchdog required: pip install 'automate-lab[watch]'"
        ) from exc

    inbox = _env_path("CSV_INBOX", Path.home() / "Downloads")
    done = _env_path("CSV_DONE", inbox / "processed")
    quarantine = _env_path("CSV_QUARANTINE", inbox / "quarantine")
    dry_run = os.environ.get("DRY_RUN", "0") == "1"

    class CsvHandler(FileSystemEventHandler):
        def __init__(self) -> None:
            self._busy: set[str] = set()

        def on_created(self, event):  # type: ignore[override]
            if event.is_directory:
                return
            self._maybe_handle(Path(event.src_path))

        def on_moved(self, event):  # type: ignore[override]
            if event.is_directory:
                return
            self._maybe_handle(Path(event.dest_path))

        def _maybe_handle(self, path: Path) -> None:
            if path.suffix.lower() in SKIP_SUFFIX:
                return
            if path.suffix.lower() != ".csv":
                return
            try:
                resolved = path.resolve()
            except OSError:
                resolved = path
            if done in resolved.parents or quarantine in resolved.parents:
                return
            key = str(resolved)
            if key in self._busy:
                return
            self._busy.add(key)
            try:
                if not wait_until_stable(path):
                    print(f"SKIP unstable {path}")
                    return
                process_csv(path, done=done, dry_run=dry_run)
            except Exception as e:
                quarantine.mkdir(parents=True, exist_ok=True)
                print(f"FAIL {path} ({type(e).__name__}: {e})")
                if not dry_run and path.exists():
                    path.replace(quarantine / path.name)
            finally:
                self._busy.discard(key)

    inbox.mkdir(parents=True, exist_ok=True)
    handler = CsvHandler()
    obs = Observer()
    obs.schedule(handler, str(inbox), recursive=False)
    obs.start()
    print(f"watching {inbox} dry_run={dry_run}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
