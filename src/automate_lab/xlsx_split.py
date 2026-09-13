"""Split each Excel sheet into its own UTF-8 CSV.

Blog: https://automate-lab.tistory.com/32
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

SAFE = re.compile(r'[\\/:*?"<>|]+')


def safe_name(sheet: str) -> str:
    name = SAFE.sub("_", sheet.strip()) or "sheet"
    return name[:80]


def split_xlsx(
    src: Path, out_dir: Path, *, skip_empty: bool = True
) -> list[Path]:
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas required: pip install 'automate-lab[xlsx]'") from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    xl = pd.ExcelFile(src, engine="openpyxl")
    written: list[Path] = []
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        if skip_empty and df.empty:
            print(f"skip empty: {sheet}")
            continue
        path = out_dir / f"{safe_name(sheet)}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        written.append(path)
        print(f"wrote {path} rows={len(df)} cols={len(df.columns)}")
    return written


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Split xlsx sheets to CSV")
    p.add_argument("--src", type=Path, default=Path("in/report.xlsx"))
    p.add_argument("--out", type=Path, default=Path("out/sheets"))
    p.add_argument("--keep-empty", action="store_true")
    args = p.parse_args(argv)
    if not args.src.exists():
        raise SystemExit(f"missing: {args.src}")
    outs = split_xlsx(
        args.src, args.out, skip_empty=not args.keep_empty
    )
    print(f"done: {len(outs)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
