"""Join two tables like Excel VLOOKUP via pandas.merge.

Blog: https://automate-lab.tistory.com/34
"""
from __future__ import annotations

import argparse
from pathlib import Path


def read_table(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas required: pip install 'automate-lab[xlsx]'") from exc

    suf = path.suffix.lower()
    if suf in {".xlsx", ".xlsm"}:
        return pd.read_excel(path, engine="openpyxl", dtype=str)
    if suf == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    raise SystemExit(f"unsupported: {path}")


def warn_key_issues(left, right, on: str) -> None:
    if on not in left.columns or on not in right.columns:
        raise SystemExit(f"key column missing: {on}")
    dup_l = int(left[on].duplicated().sum())
    dup_r = int(right[on].duplicated().sum())
    if dup_l:
        print(f"warn: left key duplicates={dup_l} (rows may explode)")
    if dup_r:
        print(f"warn: right key duplicates={dup_r} (rows may explode)")
    null_l = int(left[on].isna().sum()) + int((left[on] == "").sum())
    null_r = int(right[on].isna().sum()) + int((right[on] == "").sum())
    if null_l or null_r:
        print(f"warn: empty keys left={null_l} right={null_r}")


def merge_tables(
    left,
    right,
    *,
    on: str,
    how: str = "left",
    drop_dup_right: bool = False,
):
    warn_key_issues(left, right, on)
    r = right
    if drop_dup_right:
        before = len(r)
        r = r.drop_duplicates(subset=[on], keep="first")
        print(f"right dedupe: {before} -> {len(r)}")
    out = left.merge(r, on=on, how=how, indicator=True, suffixes=("", "_map"))
    counts = out["_merge"].value_counts().to_dict()
    print(f"merge how={how} counts={counts}")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Join two tables like VLOOKUP")
    p.add_argument("--left", type=Path, required=True)
    p.add_argument("--right", type=Path, required=True)
    p.add_argument("--on", required=True, help="join key column name")
    p.add_argument(
        "--how",
        default="left",
        choices=["left", "right", "inner", "outer"],
    )
    p.add_argument("--out", type=Path, default=Path("out/merged.csv"))
    p.add_argument("--dedupe-right", action="store_true")
    args = p.parse_args(argv)

    left = read_table(args.left)
    right = read_table(args.right)
    merged = merge_tables(
        left,
        right,
        on=args.on,
        how=args.how,
        drop_dup_right=args.dedupe_right,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(f"wrote {args.out} rows={len(merged)} cols={len(merged.columns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
