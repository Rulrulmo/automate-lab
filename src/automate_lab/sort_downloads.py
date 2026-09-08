"""Batch-sort a downloads folder by extension and filename keywords.

Blog: https://automate-lab.tistory.com/22
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

DOWNLOADS = Path.home() / "Downloads"
SORTED_ROOT = Path.home() / "SortedDownloads"
LOG_PATH = SORTED_ROOT / "sort_log.txt"

EXT_MAP = {
    ".pdf": "docs/pdf",
    ".xlsx": "sheets",
    ".xls": "sheets",
    ".csv": "sheets",
    ".png": "images",
    ".jpg": "images",
    ".jpeg": "images",
    ".webp": "images",
    ".zip": "archives",
    ".gz": "archives",
    ".7z": "archives",
}

KEYWORD_RULES = [
    (re.compile(r"(invoice|청구|세금계산서)", re.I), "finance/invoices"),
    (re.compile(r"(receipt|영수증)", re.I), "finance/receipts"),
    (re.compile(r"(screenshot|스크린샷|화면)", re.I), "images/screenshots"),
]


def destination_for(path: Path, *, sorted_root: Path) -> Path:
    name = path.name
    suffix = path.suffix.lower()
    for pattern, rel in KEYWORD_RULES:
        if pattern.search(name):
            return sorted_root / rel
    rel = EXT_MAP.get(suffix, "misc")
    return sorted_root / rel


def unique_path(dest_dir: Path, filename: str) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    n = 2
    while True:
        candidate = dest_dir / f"{stem}_{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def log(line: str, *, sorted_root: Path, log_path: Path) -> None:
    sorted_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{stamp} {line}\n")


def move_one(
    src: Path,
    *,
    sorted_root: Path,
    dry: bool,
    log_path: Path,
) -> Path | None:
    if not src.is_file():
        return None
    if src.name.endswith((".crdownload", ".part", ".tmp")):
        return None
    if src.name.startswith("."):
        return None

    dest_dir = destination_for(src, sorted_root=sorted_root)
    target = unique_path(dest_dir, src.name)
    rel = target.relative_to(sorted_root)
    if dry:
        log(f"DRY {src.name} -> {rel}", sorted_root=sorted_root, log_path=log_path)
        return target
    shutil.move(str(src), str(target))
    return target


def sort_downloads(
    *,
    downloads: Path = DOWNLOADS,
    sorted_root: Path = SORTED_ROOT,
    dry: bool = False,
) -> int:
    log_path = sorted_root / "sort_log.txt"
    if not downloads.exists():
        raise SystemExit(f"다운로드 폴더 없음: {downloads}")

    moved = 0
    for src in sorted(downloads.iterdir()):
        try:
            target = move_one(
                src, sorted_root=sorted_root, dry=dry, log_path=log_path
            )
        except OSError as e:
            log(
                f"FAIL {src.name} ({type(e).__name__}: {e})",
                sorted_root=sorted_root,
                log_path=log_path,
            )
            continue
        if target is None:
            continue
        if not dry:
            log(
                f"OK {src.name} -> {target.relative_to(sorted_root)}",
                sorted_root=sorted_root,
                log_path=log_path,
            )
        moved += 1
    return moved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sort downloads by rules")
    parser.add_argument("--downloads", type=Path, default=DOWNLOADS)
    parser.add_argument("--sorted-root", type=Path, default=SORTED_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    n = sort_downloads(
        downloads=args.downloads.expanduser(),
        sorted_root=args.sorted_root.expanduser(),
        dry=args.dry_run,
    )
    print(f"moved={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
