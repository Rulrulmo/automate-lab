"""Draft release notes from git log only (not full tree).

Blog: https://automate-lab.tistory.com/31
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from automate_lab.retry import HttpRetryError, urllib_request_with_retry


def git_log(range_rev: str, repo: Path) -> str:
    cmd = [
        "git",
        "-C",
        str(repo),
        "log",
        "--no-merges",
        "--pretty=format:%h %s",
        range_rev,
    ]
    out = subprocess.check_output(cmd, text=True)
    lines: list[str] = []
    for line in out.splitlines():
        low = line.lower()
        if " chore:" in f" {low}" or low.rstrip().endswith(" chore"):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def build_prompt(log_text: str, version: str) -> str:
    return f"""다음 git log를 바탕으로 버전 {version} 릴리스 노트 초안을 한국어 마크다운으로 작성하라.
규칙:
- 사용자/운영자 관점의 변경만 묶는다 (Added / Changed / Fixed).
- 커밋 해시는 각 항목 끝에 짧게 남겨도 된다.
- 로그에 없는 기능을 만들지 말 것.
- 비밀·내부 경로·고객 식별자는 일반화할 것.

git log:
```
{log_text}
```
"""


def call_llm(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY (or LLM_API_KEY) missing")
    base = os.environ.get(
        "OPENAI_BASE_URL",
        os.environ.get("LLM_API_URL", "https://api.openai.com/v1"),
    ).rstrip("/")
    if base.endswith("/chat/completions"):
        url = base
    else:
        url = f"{base}/chat/completions"
    model = os.environ.get(
        "LLM_MODEL", os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    )
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "You draft release notes. Do not invent features.",
            },
            {"role": "user", "content": prompt},
        ],
    }
    status, raw = urllib_request_with_retry(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
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
    p = argparse.ArgumentParser(description="Release notes from git log")
    p.add_argument("--repo", type=Path, default=Path("."))
    p.add_argument("--range", dest="rev_range", default="HEAD")
    p.add_argument("--version", default="X.Y.Z")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("release-notes-prompt.txt"),
    )
    p.add_argument(
        "--call-llm",
        action="store_true",
        help="also call LLM and print draft",
    )
    args = p.parse_args(argv)

    log_text = git_log(args.rev_range, args.repo)
    if not log_text.strip():
        raise SystemExit("empty git log for given range")
    prompt = build_prompt(log_text, args.version)
    args.output.write_text(prompt, encoding="utf-8")
    print(f"wrote {args.output} ({len(log_text.splitlines())} commits)")
    if args.call_llm:
        print(call_llm(prompt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
