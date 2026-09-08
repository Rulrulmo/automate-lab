"""Map messy CSV headers to a canonical schema (synonyms then LLM).

Blog: https://automate-lab.tistory.com/23
Uses stdlib urllib + automate_lab.retry (no requests required).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

from automate_lab.retry import HttpRetryError, urllib_request_with_retry

CANONICAL = [
    "date",
    "vendor",
    "amount",
    "currency",
    "memo",
]

SYNONYMS = {
    "date": {"date", "날짜", "거래일", "일자", "trx_date"},
    "vendor": {"vendor", "거래처", "거래처명", "supplier", "고객명"},
    "amount": {"amount", "금액", "매출액", "공급가액", "합계", "total"},
    "currency": {"currency", "통화", "화폐", "curr"},
    "memo": {"memo", "비고", "적요", "description", "note"},
}


def read_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        row = next(csv.reader(f))
    return [c.strip() for c in row]


def local_map(headers: list[str]) -> tuple[dict[str, str], list[str]]:
    mapping: dict[str, str] = {}
    unresolved: list[str] = []
    used: set[str] = set()

    for raw in headers:
        key = raw.strip().lower()
        hit = None
        for canon, words in SYNONYMS.items():
            if key in {w.lower() for w in words}:
                hit = canon
                break
        if hit and hit not in used:
            mapping[raw] = hit
            used.add(hit)
        else:
            unresolved.append(raw)
    return mapping, unresolved


def cache_key(headers: list[str]) -> str:
    blob = "|".join(headers)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def llm_map(unresolved: list[str], already: dict[str, str]) -> dict[str, str]:
    if not unresolved:
        return {}

    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    key = os.environ["OPENAI_API_KEY"]

    remaining = [c for c in CANONICAL if c not in already.values()]
    system = (
        "당신은 CSV 헤더 매핑기다. JSON만 반환한다. "
        "추측이 낮으면 그 헤더를 skip 목록에 넣는다. "
        "표준에 없는 새 이름을 만들지 않는다."
    )
    user = {
        "canonical_remaining": remaining,
        "unresolved_headers": unresolved,
        "already_mapped": already,
        "output_schema": {
            "mapping": {"raw_header": "canonical_or_omit"},
            "skip": ["raw_header"],
            "confidence": "high|medium|low",
        },
    }
    payload = {
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
    }
    status, body = urllib_request_with_retry(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
        timeout=60.0,
        max_attempts=5,
    )
    if status != 200:
        raise HttpRetryError(f"unexpected status {status}", status=status, body=body.decode())
    content = json.loads(body.decode("utf-8"))["choices"][0]["message"]["content"]
    data = json.loads(content)

    out: dict[str, str] = {}
    for raw, canon in (data.get("mapping") or {}).items():
        if raw in unresolved and canon in remaining and canon not in out.values():
            out[raw] = canon
    return out


def build_mapping(path: Path) -> dict:
    headers = read_header(path)
    mapping, unresolved = local_map(headers)
    error = None
    try:
        mapping.update(llm_map(unresolved, mapping))
    except Exception as e:
        error = f"{type(e).__name__}: {e}"

    still = [h for h in headers if h not in mapping]
    review = {
        "file": str(path),
        "cache_key": cache_key(headers),
        "mapping": dict(mapping),
        "unmapped": still,
        "error": error,
    }
    review_path = path.with_suffix(path.suffix + ".mapping.json")
    review_path.write_text(
        json.dumps(review, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return review


def rewrite_csv(src: Path, dest: Path, mapping: dict[str, str]) -> None:
    with src.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    fieldnames = list(CANONICAL)
    with dest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = {c: "" for c in fieldnames}
            for raw, val in row.items():
                canon = mapping.get(raw)
                if canon in out:
                    out[canon] = (val or "").strip()
            writer.writerow(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Map CSV headers to canonical columns")
    parser.add_argument("csv", type=Path, nargs="?", default=Path("input.csv"))
    args = parser.parse_args(argv)
    src = args.csv
    if not src.exists():
        print(f"missing file: {src}", file=sys.stderr)
        return 1

    review = build_mapping(src)
    mapping = review["mapping"]
    if review["unmapped"]:
        print("review needed:", review["unmapped"])
        print("edit", src.with_suffix(src.suffix + ".mapping.json"))
        return 2

    dest = src.with_name(src.stem + "_normalized.csv")
    rewrite_csv(src, dest, mapping)
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
