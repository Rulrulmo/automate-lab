"""Draft Conventional Commit messages from git diff only.

Blog: https://automate-lab.tistory.com/27
Uses stdlib urllib + automate_lab.retry. Never runs git commit.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

from automate_lab.retry import HttpRetryError, urllib_request_with_retry

BLOCK_PAT = re.compile(r"(\.env|credentials|id_rsa|\.pem|secrets?)", re.I)
SKIP_SUFFIX = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
}
MAX_CHARS = 20000

SYSTEM = """당신은 시니어 개발자다. 주어진 git diff만 보고 Conventional Commits 형식의
커밋 메시지 초안을 한국어 또는 영어 한 가지로 작성한다.
규칙:
- 첫 줄: type(scope): summary (50자 내외)
- 필요하면 본문 1~3줄. 추측하지 말고 diff에 있는 사실만.
- 코드블록·따옴표·설명 문장 없이 메시지 본문만 출력.
"""


def run_git(args: list[str]) -> str:
    p = subprocess.run(["git", *args], check=False, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr.strip() or "git failed")
    return p.stdout


def collect_diff(*, staged: bool) -> str:
    args = ["diff", "--cached"] if staged else ["diff", "HEAD"]
    return run_git(args)


def blocked_paths(diff: str) -> list[str]:
    hit: list[str] = []
    for line in diff.splitlines():
        if line.startswith("+++ b/") or line.startswith("--- a/"):
            path = line[6:]
            base = path.rsplit("/", 1)[-1]
            if BLOCK_PAT.search(path) or base in SKIP_SUFFIX:
                hit.append(path)
    return sorted(set(hit))


def call_llm(diff: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY missing")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("COMMIT_MODEL", os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"))
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": f"다음 diff로 커밋 메시지 초안만 작성하라:\n\n{diff}",
            },
        ],
    }
    status, raw = urllib_request_with_retry(
        f"{base.rstrip('/')}/chat/completions",
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
    parser = argparse.ArgumentParser(description="Draft commit message from git diff")
    parser.add_argument("--staged", "-s", action="store_true")
    args = parser.parse_args(argv)

    diff = collect_diff(staged=args.staged)
    if not diff.strip():
        print("empty diff", file=sys.stderr)
        return 1

    bad = blocked_paths(diff)
    if bad:
        print("blocked paths:", file=sys.stderr)
        for p in bad:
            print(f"  {p}", file=sys.stderr)
        return 2

    if len(diff) > MAX_CHARS:
        print(
            f"diff too large: {len(diff)} chars (max {MAX_CHARS})",
            file=sys.stderr,
        )
        print("file list only — write the message manually", file=sys.stderr)
        name_args = (
            ["diff", "--cached", "--name-only"]
            if args.staged
            else ["diff", "HEAD", "--name-only"]
        )
        print(run_git(name_args))
        return 3

    print(call_llm(diff))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
