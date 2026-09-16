"""Diff two CSVs by key columns into added/removed/changed.

Blog: https://automate-lab.tistory.com/38
"""
from __future__ import annotations

import argparse
from pathlib import Path


def read_csv(path: Path):
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas required: pip install 'automate-lab[xlsx]'") from exc
    return pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")


def normalize(df):
    out = df.copy()
    for c in out.columns:
        out[c] = out[c].astype(str).str.strip()
    return out


def require_keys(df, keys: list[str], label: str) -> None:
    missing = [k for k in keys if k not in df.columns]
    if missing:
        raise SystemExit(f"{label}: key column missing: {missing}")


def warn_duplicate_keys(df, keys: list[str], label: str) -> None:
    dup = int(df.duplicated(subset=keys, keep=False).sum())
    if dup:
        print(f"warn: {label} has {dup} rows in duplicate-key groups on {keys}")


def diff_frames(left, right, keys: list[str]):
    import pandas as pd

    require_keys(left, keys, "left")
    require_keys(right, keys, "right")
    left = normalize(left)
    right = normalize(right)
    warn_duplicate_keys(left, keys, "left")
    warn_duplicate_keys(right, keys, "right")

    left_u = left.drop_duplicates(subset=keys, keep="first").set_index(keys, drop=False)
    right_u = right.drop_duplicates(subset=keys, keep="first").set_index(keys, drop=False)

    left_ids = set(left_u.index)
    right_ids = set(right_u.index)
    added_ids = right_ids - left_ids
    removed_ids = left_ids - right_ids
    common = left_ids & right_ids

    added = (
        right_u.loc[list(added_ids)].reset_index(drop=True)
        if added_ids
        else right_u.iloc[0:0].reset_index(drop=True)
    )
    removed = (
        left_u.loc[list(removed_ids)].reset_index(drop=True)
        if removed_ids
        else left_u.iloc[0:0].reset_index(drop=True)
    )

    changed_rows: list[dict] = []
    all_cols = list(dict.fromkeys(list(left.columns) + list(right.columns)))
    value_cols = [c for c in all_cols if c not in keys]

    for kid in common:
        lrow = left_u.loc[kid]
        rrow = right_u.loc[kid]
        if isinstance(lrow, pd.DataFrame):
            lrow = lrow.iloc[0]
        if isinstance(rrow, pd.DataFrame):
            rrow = rrow.iloc[0]
        diffs: list[str] = []
        for c in value_cols:
            lv = str(lrow[c]).strip() if c in lrow.index else ""
            rv = str(rrow[c]).strip() if c in rrow.index else ""
            if lv != rv:
                diffs.append(f"{c}:{lv}→{rv}")
        if diffs:
            rec: dict = {}
            if isinstance(kid, tuple):
                for i, k in enumerate(keys):
                    rec[k] = kid[i]
            else:
                rec[keys[0]] = kid
            rec["diff_summary"] = "; ".join(diffs)
            for c in value_cols:
                rec[f"before_{c}"] = str(lrow[c]).strip() if c in lrow.index else ""
                rec[f"after_{c}"] = str(rrow[c]).strip() if c in rrow.index else ""
            changed_rows.append(rec)

    changed = pd.DataFrame(changed_rows)
    print(
        f"counts added={len(added)} removed={len(removed)} changed={len(changed)} "
        f"common={len(common)}"
    )
    return added, removed, changed


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Diff two CSVs by key columns")
    p.add_argument("--left", type=Path, required=True, help="이전 CSV")
    p.add_argument("--right", type=Path, required=True, help="이후 CSV")
    p.add_argument(
        "--keys",
        required=True,
        help="콤마 구분 키 컬럼. 예: id 또는 customer_id,sku",
    )
    p.add_argument("--outdir", type=Path, default=Path("out/csv-diff"))
    p.add_argument("--excel", action="store_true", help="3시트 xlsx도 저장")
    args = p.parse_args(argv)

    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    if not keys:
        raise SystemExit("--keys is empty")

    left = read_csv(args.left)
    right = read_csv(args.right)
    added, removed, changed = diff_frames(left, right, keys)

    args.outdir.mkdir(parents=True, exist_ok=True)
    added_path = args.outdir / "added.csv"
    removed_path = args.outdir / "removed.csv"
    changed_path = args.outdir / "changed.csv"
    added.to_csv(added_path, index=False, encoding="utf-8-sig")
    removed.to_csv(removed_path, index=False, encoding="utf-8-sig")
    changed.to_csv(changed_path, index=False, encoding="utf-8-sig")
    print(f"wrote {added_path}")
    print(f"wrote {removed_path}")
    print(f"wrote {changed_path}")

    if args.excel:
        import pandas as pd

        xlsx = args.outdir / "diff.xlsx"
        with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
            added.to_excel(w, sheet_name="added", index=False)
            removed.to_excel(w, sheet_name="removed", index=False)
            changed.to_excel(w, sheet_name="changed", index=False)
        print(f"wrote {xlsx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
