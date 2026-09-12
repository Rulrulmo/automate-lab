"""Read CSV trying UTF-8 / CP949 candidates.

Blog: https://automate-lab.tistory.com/30
"""
from __future__ import annotations

import argparse
import csv
from io import StringIO
from pathlib import Path
from typing import Iterable

CANDIDATES: tuple[str, ...] = ("utf-8-sig", "utf-8", "cp949", "euc-kr")


def decode_csv_bytes(
    raw: bytes, encodings: Iterable[str] = CANDIDATES
) -> tuple[str, str]:
    last_err: Exception | None = None
    for enc in encodings:
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError as e:
            last_err = e
            continue
    assert last_err is not None
    raise UnicodeDecodeError(
        getattr(last_err, "encoding", "unknown") or "unknown",
        raw,
        getattr(last_err, "start", 0),
        getattr(last_err, "end", 1),
        f"no candidate worked among {list(encodings)}",
    )


def read_csv_auto(path: Path, **kwargs):
    """Return (DataFrame|list[dict], encoding). Uses pandas if installed."""
    raw = path.read_bytes()
    if not raw.strip():
        raise ValueError(f"empty csv: {path}")
    text, enc = decode_csv_bytes(raw)
    try:
        import pandas as pd

        df = pd.read_csv(StringIO(text), **kwargs)
        return df, enc
    except ImportError:
        reader = csv.DictReader(StringIO(text))
        rows = list(reader)
        return rows, enc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read CSV with encoding fallback")
    parser.add_argument("csv", type=Path, nargs="?", default=Path("sample.csv"))
    args = parser.parse_args(argv)
    if not args.csv.exists():
        raise SystemExit(f"missing: {args.csv}")
    data, enc = read_csv_auto(args.csv)
    if hasattr(data, "columns"):
        print(f"encoding={enc} rows={len(data)} cols={list(data.columns)[:8]}")
        print(data.head(3).to_string(index=False))
    else:
        cols = list(data[0].keys()) if data else []
        print(f"encoding={enc} rows={len(data)} cols={cols[:8]}")
        for row in data[:3]:
            print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
