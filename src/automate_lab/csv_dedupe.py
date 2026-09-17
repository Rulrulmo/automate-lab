"""Drop duplicate rows by key columns (CSV or xlsx).

Blog: https://automate-lab.tistory.com/40
"""
from __future__ import annotations

import argparse
from pathlib import Path


def read_table(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas required: pip install 'automate-lab[xlsx]'") from exc

    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xlsm"}:
        df = pd.read_excel(path, dtype=str, engine="openpyxl")
    elif suffix == ".csv":
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    else:
        raise SystemExit(f"unsupported file type: {suffix}")
    return df.fillna("")


def normalize(df, keys: list[str]):
    out = df.copy()
    for c in out.columns:
        out[c] = out[c].astype(str).str.strip()
    missing = [k for k in keys if k not in out.columns]
    if missing:
        raise SystemExit(f"key column missing: {missing}")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Drop duplicate rows by key columns")
    p.add_argument("--input", type=Path, required=True, help="CSV 또는 xlsx")
    p.add_argument(
        "--keys",
        required=True,
        help="콤마 구분 키 컬럼. 예: id 또는 order_id,sku",
    )
    p.add_argument(
        "--keep",
        choices=("first", "last"),
        default="first",
        help="남길 행 (기본 first)",
    )
    p.add_argument("--outdir", type=Path, default=Path("out/drop-duplicates"))
    p.add_argument(
        "--report",
        action="store_true",
        help="제거된 중복 행을 duplicates_report.csv로 저장",
    )
    args = p.parse_args(argv)

    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        raise SystemExit("--keys is empty")

    df = normalize(read_table(args.input), keys)
    before = len(df)

    dup_mask = df.duplicated(subset=keys, keep=False)
    cleaned = df.drop_duplicates(subset=keys, keep=args.keep)
    after = len(cleaned)
    removed = before - after

    args.outdir.mkdir(parents=True, exist_ok=True)
    cleaned_path = args.outdir / "cleaned.csv"
    cleaned.to_csv(cleaned_path, index=False, encoding="utf-8-sig")
    print(f"rows before={before} after={after} removed={removed} keep={args.keep}")
    print(f"wrote {cleaned_path}")

    if args.report:
        kept_idx = cleaned.index
        report = df.loc[dup_mask & ~df.index.isin(kept_idx)].copy()
        report_path = args.outdir / "duplicates_report.csv"
        report.to_csv(report_path, index=False, encoding="utf-8-sig")
        print(f"wrote {report_path} rows={len(report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
