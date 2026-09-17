"""Collect ERROR/CRITICAL log lines into a CSV (stdlib only).

Blog: https://automate-lab.tistory.com/41
Never modifies or deletes source logs.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

LEVEL_RE = re.compile(r"\b(ERROR|CRITICAL)\b")


def iter_log_files(root: Path, date: str | None) -> list[Path]:
    files: list[Path] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".log", ".txt", ".out"}:
            continue
        if date and date not in p.name:
            continue
        files.append(p)
    return files


def scan_file(path: Path, max_msg: int) -> list[dict]:
    rows: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"warn: utf-8 failed, replace: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"warn: skip {path}: {e}")
        return rows

    for i, line in enumerate(text.splitlines(), start=1):
        m = LEVEL_RE.search(line)
        if not m:
            continue
        msg = line.strip()
        if len(msg) > max_msg:
            msg = msg[: max_msg - 3] + "..."
        rows.append(
            {
                "path": str(path),
                "line_no": i,
                "level": m.group(1),
                "message": msg,
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Collect ERROR/CRITICAL lines to CSV")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--logs-dir", type=Path, help="로그 폴더")
    g.add_argument("--file", type=Path, help="단일 로그 파일")
    p.add_argument("--out", type=Path, default=Path("out/errors.csv"))
    p.add_argument("--date", default=None, help="파일명에 포함된 YYYYMMDD")
    p.add_argument("--max-msg", type=int, default=500, help="message 최대 길이")
    args = p.parse_args(argv)

    if args.file:
        files = [args.file]
        if not args.file.is_file():
            raise SystemExit(f"not a file: {args.file}")
    else:
        if not args.logs_dir.is_dir():
            raise SystemExit(f"not a directory: {args.logs_dir}")
        files = iter_log_files(args.logs_dir, args.date)

    all_rows: list[dict] = []
    for f in files:
        all_rows.extend(scan_file(f, args.max_msg))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=["path", "line_no", "level", "message"])
        w.writeheader()
        w.writerows(all_rows)

    print(f"files={len(files)} hits={len(all_rows)} wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
