"""Find same-size, same-SHA256 file candidates without deleting any files."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import stat
from collections import defaultdict
from pathlib import Path


def signature(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def sha256_file(path: Path, expected: tuple) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        if signature(os.fstat(stream.fileno())) != expected:
            raise ValueError(f"File changed before reading: {path}")
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
        if signature(os.fstat(stream.fileno())) != expected:
            raise ValueError(f"File changed while reading: {path}")
    if signature(path.lstat()) != expected:
        raise ValueError(f"File changed after reading: {path}")
    return digest.hexdigest()


def find_duplicates(root: Path) -> list[dict]:
    """Return duplicate candidates. Symlinks and repeated hard links are skipped.

    SHA-256 matching is not a byte-by-byte proof. Scan a stable local folder;
    this does not lock files or provide a filesystem snapshot.
    """
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f"Not a folder: {root}")
    sizes = defaultdict(list)
    seen = set()

    def fail(error):
        raise error

    for folder, dirs, names in os.walk(root, followlinks=False, onerror=fail):
        dirs[:] = sorted(d for d in dirs if not (Path(folder) / d).is_symlink())
        for name in sorted(names):
            path = Path(folder) / name
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                continue
            identity = (info.st_dev, info.st_ino)
            if identity in seen:
                continue
            seen.add(identity)
            sizes[info.st_size].append((path, signature(info)))

    groups = []
    for size, items in sorted(sizes.items()):
        if len(items) < 2:
            continue
        hashes = defaultdict(list)
        for path, expected in sorted(items):
            hashes[sha256_file(path, expected)].append(path)
        for digest, paths in sorted(hashes.items()):
            if len(paths) > 1:
                groups.append({"size_bytes": size, "sha256": digest,
                               "paths": [str(p.relative_to(root)) for p in paths]})
    return groups


def write_report(root: Path, output: Path, groups: list[dict]) -> None:
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.is_relative_to(root):
        raise ValueError("Write the CSV outside the input folder")
    # Exclusive creation prevents replacing an existing report or other file.
    with output.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["group", "size_bytes", "sha256", "relative_path"])
        for number, group in enumerate(groups, 1):
            for path in group["paths"]:
                # Spreadsheet programs can interpret path text as a formula.
                safe_path = "'" + path if path.startswith(("=", "+", "-", "@", "\t", "\r", "\n")) else path
                writer.writerow([number, group["size_bytes"], group["sha256"], safe_path])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List duplicate file candidates; never delete")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.out.resolve().is_relative_to(args.input.resolve()):
            raise ValueError("Write the CSV outside the input folder")
        if args.out.exists():
            raise FileExistsError(f"Report already exists: {args.out}")
        groups = find_duplicates(args.input)
        write_report(args.input, args.out, groups)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")
    print(f"groups={len(groups)} candidate_files={sum(len(g['paths']) for g in groups)}")
    print(f"report={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
