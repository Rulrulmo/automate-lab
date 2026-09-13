"""Extract pytest failure mid and summarize with LLM.

Blog: https://automate-lab.tistory.com/33
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

MAX_CHARS = 8000
FAIL_SPLIT = re.compile(r"={10,}\s*FAILURES\s*={10,}")
NEXT_SECTION = re.compile(
    r"={10,}\s*(?:short test summary info|warnings summary)\s*={10,}",
    re.I,
)


def run_pytest(log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(
            ["pytest", "-q", "--tb=short"],
            stdout=fh,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return proc.returncode


def extract_failures(log_text: str) -> str:
    m = FAIL_SPLIT.search(log_text)
    if not m:
        lines = [
            ln
            for ln in log_text.splitlines()
            if "FAILED" in ln or "ERROR" in ln
        ]
        body = "\n".join(lines[-80:])
        return body[-MAX_CHARS:]
    start = m.end()
    m2 = NEXT_SECTION.search(log_text, start)
    body = log_text[start : m2.start() if m2 else None].strip()
    if len(body) > MAX_CHARS:
        body = body[-MAX_CHARS:]
    return body


def build_prompt(failure_mid: str) -> str:
    return textwrap.dedent(
        f"""
        당신은 테스트 실패 로그를 읽는 시니어 개발자다.
        아래는 pytest 실패 mid다. 추측임을 분명히 하고,
        1) 공통 원인 후보 2~3개 2) 확인 순서 3) 먼저 볼 파일/함수
        만 짧게 한국어로 적어라. 코드를 새로 작성하지 마라.

        --- pytest failures ---
        {failure_mid}
        """
    ).strip()


def call_llm(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY missing")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "Be concise. No secrets. Mark uncertainty.",
            },
            {"role": "user", "content": prompt},
        ],
    }
    status, raw = urllib_request_with_retry(
        f"{base}/chat/completions",
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
    p = argparse.ArgumentParser(description="Summarize pytest failures")
    p.add_argument("--log", type=Path, default=Path("out/pytest.log"))
    p.add_argument("--out", type=Path, default=Path("out/pytest_failure_summary.md"))
    p.add_argument("--skip-run", action="store_true", help="use existing --log only")
    args = p.parse_args(argv)

    if not args.skip_run:
        code = run_pytest(args.log)
    else:
        if not args.log.exists():
            raise SystemExit(f"missing log: {args.log}")
        code = 1

    text = args.log.read_text(encoding="utf-8", errors="replace")
    if not args.skip_run and code == 0:
        print("all tests passed; skip LLM")
        return 0

    mid = extract_failures(text)
    if not mid.strip():
        raise SystemExit("no failure mid extracted; check pytest output format")
    summary = call_llm(build_prompt(mid))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(summary + "\n", encoding="utf-8")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
