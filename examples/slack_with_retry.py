"""Slack webhook notify with retry — blog companion.

Requires SLACK_WEBHOOK_URL. Never commit the URL.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from automate_lab.retry import HttpRetryError, post_json

logging.basicConfig(level=logging.INFO)


def notify_slack(text: str) -> None:
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        raise RuntimeError("SLACK_WEBHOOK_URL is not set")
    status, body = post_json(url, {"text": text}, timeout=10.0, max_attempts=5)
    decoded = body.decode("utf-8", errors="replace").strip()
    if decoded != "ok":
        raise RuntimeError(f"unexpected slack body: {body!r} status={status}")


if __name__ == "__main__":
    try:
        notify_slack("automate-lab retry wrapper smoke test")
        print("sent")
    except HttpRetryError as e:
        print("failed after retries:", e)
