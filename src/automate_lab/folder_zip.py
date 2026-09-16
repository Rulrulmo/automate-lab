"""Zip a folder into backups/YYYYMMDD_HHMMSS_name.zip (stdlib only).

Blog: https://automate-lab.tistory.com/39
Never deletes the source tree — only optional prune of old zips.
"""
from __future__ import annotations

import argparse
import fnmatch
import zipfile
from datetime import datetime
from pathlib import Path

DEFAULT_EXCLUDES = [
    "__pycache__",
    ".git",
    ".svn",
    ".hg",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "Thumbs.db",
]


def parse_excludes(extra: list[str] | None) -> list[str]:
    pats = list(DEFAULT_EXCLUDES)
    if extra:
        for item in extra:
            for part in item.split(","):
                part = part.strip()
                if part:
                    pats.append(part)
    return pats


def should_exclude(rel: Path, patterns: list[str]) -> bool:
    parts = rel.parts
    name = rel.name
    for pat in patterns:
        if any(fnmatch.fnmatch(p, pat) for p in parts):
            return True
        if fnmatch.fnmatch(name, pat):
            return True
        if fnmatch.fnmatch(str(rel).replace("\\", "/"), pat):
            return True
    return False


def collect_files(source: Path, patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(source)
        if should_exclude(rel, patterns):
            continue
        files.append(path)
    return files


def make_zip_name(
    backup_dir: Path, label: str, when: datetime | None = None
) -> Path:
    when = when or datetime.now()
    stamp = when.strftime("%Y%m%d_%H%M%S")
    safe = (
        "".join(c if c.isalnum() or c in "-_" else "_" for c in label).strip("_")
        or "backup"
    )
    return backup_dir / f"{stamp}_{safe}.zip"


def write_zip(source: Path, files: list[Path], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = path.relative_to(source).as_posix()
            zf.write(path, arcname)


def prune_old(backup_dir: Path, label: str, keep: int) -> None:
    if keep < 1:
        raise SystemExit("--keep must be >= 1")
    safe = (
        "".join(c if c.isalnum() or c in "-_" else "_" for c in label).strip("_")
        or "backup"
    )
    candidates = sorted(
        backup_dir.glob(f"*_{safe}.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for old in candidates[keep:]:
        old.unlink()
        print(f"removed old zip: {old}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Zip a folder into backups/YYYYMMDD_HHMMSS_name.zip"
    )
    p.add_argument("--source", type=Path, required=True, help="백업할 폴더")
    p.add_argument("--backup-dir", type=Path, default=Path("backups"))
    p.add_argument("--name", default="", help="zip 이름 접미. 기본은 소스 폴더명")
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="제외 패턴. 여러 번 주거나 콤마로 나열",
    )
    p.add_argument(
        "--keep",
        type=int,
        default=0,
        help="같은 이름 zip을 N개만 유지 (0이면 정리 안 함)",
    )
    args = p.parse_args(argv)

    source = args.source.resolve()
    if not source.is_dir():
        raise SystemExit(f"not a directory: {source}")

    label = args.name.strip() or source.name
    patterns = parse_excludes(args.exclude)
    files = collect_files(source, patterns)
    if not files:
        raise SystemExit(f"source empty or all excluded: {source}")

    dest = make_zip_name(args.backup_dir, label)
    write_zip(source, files, dest)
    print(f"wrote {dest} files={len(files)}")

    if args.keep > 0:
        prune_old(args.backup_dir, label, args.keep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
