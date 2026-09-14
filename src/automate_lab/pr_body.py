"""Draft PR body from gh pr diff only.

Blog: https://automate-lab.tistory.com/35
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import textwrap
from pathlib import Path

from automate_lab.retry import HttpRetryError, urllib_request_with_retry

MAX_CHARS = 12_000
SECRETISH = re.compile(
    r"(?i)(api[_-]?key|secret|token|password|authorization:\s*\S+)"
)


def run_gh_pr_diff(pr: str | None) -> str:
    cmd = ["gh", "pr", "diff"]
    if pr:
        cmd.append(pr)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise SystemExit(f"gh pr diff failed: {err}")
    return proc.stdout


def truncate(diff: str, limit: int = MAX_CHARS) -> str:
    if len(diff) <= limit:
        return diff
    head_note = f"... truncated {len(diff) - limit} chars ...\n"
    return head_note + diff[-limit:]


def scrub_hint(diff: str) -> None:
    if SECRETISH.search(diff):
        print(
            "warn: diff may contain secret-like strings; "
            "review before sending to LLM"
        )


def build_prompt(diff_mid: str, title_hint: str | None) -> str:
    title_line = f"PR title hint: {title_hint}\n" if title_hint else ""
    return textwrap.dedent(
        f"""
        당신은 코드 리뷰어다. 아래는 GitHub PR의 unified diff mid다.
        시크릿·토큰·개인정보를 반복하지 마라.
        한국어 마크다운으로만 답하라.

        형식:

        ## Summary
        - (변경 요지 2~5개 불릿)

        ## Test plan
        - [ ] (검증 항목)

        추측이면 추측이라고 밝혀라. 코드를 새로 작성하지 마라.

        {title_line}
        --- diff ---
        {diff_mid}
        """
    ).strip()


def call_llm(prompt: str) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY not set")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "Draft only. No secrets. Mark uncertainty.",
            },
            {"role": "user", "content": prompt},
        ],
    }
    status, raw = urllib_request_with_retry(
        f"{base}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
        timeout=60.0,
        max_attempts=5,
    )
    if status != 200:
        raise HttpRetryError(
            f"unexpected status {status}", status=status, body=raw.decode()
        )
    data = json.loads(raw.decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Draft PR body from gh pr diff")
    p.add_argument("--pr", default=None, help="PR number or URL (optional)")
    p.add_argument("--title-hint", default=None)
    p.add_argument("--out", type=Path, default=Path("out/pr_body_draft.md"))
    p.add_argument("--max-chars", type=int, default=MAX_CHARS)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="write prompt only, skip LLM",
    )
    args = p.parse_args(argv)

    raw = run_gh_pr_diff(args.pr)
    if not raw.strip():
        raise SystemExit("empty diff; nothing to draft")
    scrub_hint(raw)
    mid = truncate(raw, args.max_chars)
    prompt = build_prompt(mid, args.title_hint)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        Path(str(args.out) + ".prompt.txt").write_text(prompt, encoding="utf-8")
        print(f"dry-run prompt chars={len(prompt)}")
        return 0
    body = call_llm(prompt)
    args.out.write_text(body.rstrip() + "\n", encoding="utf-8")
    print(body)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
