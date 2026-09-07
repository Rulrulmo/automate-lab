"""Watch a folder for new CSV files and process after size stabilizes.

Blog: https://automate-lab.tistory.com/18
"""
from __future__ import annotations

import argparse
import csv
import shutil
import time
from pathlib import Path

STABLE_SECONDS = 1.5
STABLE_CHECKS = 3


def wait_until_stable(path: Path) -> bool:
    """True when file size is unchanged for a short window."""
    last_size = -1
    same_count = 0
    for _ in range(40):
        if not path.exists():
            return False
        try:
            size = path.stat().st_size
        except OSError:
            return False
        if size == last_size and size > 0:
            same_count += 1
            if same_count >= STABLE_CHECKS:
                return True
        else:
            same_count = 0
            last_size = size
        time.sleep(STABLE_SECONDS)
    return False


def is_temp_name(name: str) -> bool:
    lower = name.lower()
    if name.startswith("~$") or name.startswith("."):
        return True
    if lower.endswith(".crdownload") or lower.endswith(".part"):
        return True
    if lower.endswith(".tmp"):
        return True
    return False


def process_csv(path: Path, done_dir: Path) -> None:
    """Replace this with your business logic. Default: count rows, then move."""
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0] if rows else []
    body = rows[1:] if len(rows) > 1 else []
    print(f"[ok] {path.name}: columns={len(header)} rows={len(body)}")

    done_dir.mkdir(parents=True, exist_ok=True)
    target = done_dir / path.name
    if target.exists():
        stem, suffix = path.stem, path.suffix
        target = done_dir / f"{stem}_{int(time.time())}{suffix}"
    shutil.move(str(path), str(target))
    print(f"[moved] {target}")


def main() -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as exc:
        raise SystemExit(
            "watchdog is required: pip install 'automate-lab[watch]'"
        ) from exc

    class CsvHandler(FileSystemEventHandler):
        def __init__(self, done_dir: Path) -> None:
            super().__init__()
            self.done_dir = done_dir
            self._seen: set[str] = set()

        def on_created(self, event) -> None:  # type: ignore[override]
            if event.is_directory:
                return
            self._maybe_handle(Path(event.src_path))

        def on_moved(self, event) -> None:  # type: ignore[override]
            if event.is_directory:
                return
            self._maybe_handle(Path(event.dest_path))

        def _maybe_handle(self, path: Path) -> None:
            if path.suffix.lower() != ".csv":
                return
            if is_temp_name(path.name):
                return
            key = str(path.resolve()) if path.exists() else str(path)
            if key in self._seen:
                return
            self._seen.add(key)
            if not wait_until_stable(path):
                print(f"[skip] not stable: {path.name}")
                self._seen.discard(key)
                return
            try:
                process_csv(path, self.done_dir)
            except Exception as err:  # keep watcher alive
                print(f"[error] {path.name}: {err}")

    parser = argparse.ArgumentParser(description="Watch a folder for new CSV files")
    parser.add_argument(
        "--watch",
        type=Path,
        default=Path.home() / "Downloads",
        help="Folder to watch",
    )
    parser.add_argument(
        "--done",
        type=Path,
        default=Path.home() / "Downloads" / "processed_csv",
        help="Folder to move processed files into",
    )
    args = parser.parse_args()
    watch_dir = args.watch.expanduser().resolve()
    done_dir = args.done.expanduser().resolve()
    if not watch_dir.is_dir():
        raise SystemExit(f"watch dir not found: {watch_dir}")

    handler = CsvHandler(done_dir)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    print(f"watching: {watch_dir}")
    print(f"done dir: {done_dir}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
