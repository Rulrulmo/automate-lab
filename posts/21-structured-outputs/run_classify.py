"""Log classification example — https://automate-lab.tistory.com/21

Requires OPENAI_API_KEY and: pip install 'automate-lab[structured]'
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from automate_lab.structured import apply_policy, classify_line


def looks_like_error(line: str) -> bool:
    upper = line.upper()
    return any(
        k in upper
        for k in ("ERROR", "EXCEPTION", "TIMEOUT", "TRACEBACK", "HTTP 5")
    )


def main() -> None:
    sample = Path(__file__).with_name("sample_batch.log")
    if not sample.exists():
        sample.write_text(
            "\n".join(
                [
                    "INFO job started",
                    "ERROR csv-merge failed: ConnectionResetError after 30s to db-primary",
                    "WARNING slack webhook HTTP 429",
                    "ERROR invalid column 'amt' in store_a.csv",
                ]
            ),
            encoding="utf-8",
        )

    rows = []
    for raw in sample.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or not looks_like_error(line):
            continue
        result = apply_policy(classify_line(line[:1000]))
        rows.append((line, result))

    retryable_rows = [(line, r) for line, r in rows if r.retryable]
    print(f"classified={len(rows)} retryable={len(retryable_rows)}")
    for line, r in rows:
        print(
            f"- {r.severity.value:8} retryable={r.retryable} "
            f"component={r.component} :: {r.reason}"
        )
        print(f"  log: {line[:80]}")


if __name__ == "__main__":
    main()
