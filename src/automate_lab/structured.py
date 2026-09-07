"""Structured Outputs helpers for log classification.

Blog: https://automate-lab.tistory.com/21
"""
from __future__ import annotations

import os
from enum import Enum


class Severity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


def _models():
    try:
        from openai import OpenAI
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise ImportError(
            "openai and pydantic are required: pip install 'automate-lab[structured]'"
        ) from exc
    return OpenAI, BaseModel, Field


def log_classification_model():
    """Build LogClassification Pydantic model (lazy import)."""
    _, BaseModel, Field = _models()

    class LogClassification(BaseModel):
        severity: Severity
        component: str = Field(
            description="Suspected component, e.g. db, slack, csv-merge, unknown",
            min_length=1,
            max_length=64,
        )
        retryable: bool = Field(
            description="True when the same input is worth retrying"
        )
        reason: str = Field(
            description="Short reason grounded in the log; do not invent facts",
            max_length=200,
        )

    return LogClassification


def classify_line(line: str, *,
                  model: str | None = None,
                  api_key: str | None = None):
    """Classify one log line into a fixed schema via Structured Outputs."""
    OpenAI, _, _ = _models()
    LogClassification = log_classification_model()
    client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])
    model_name = model or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

    completion = client.beta.chat.completions.parse(
        model=model_name,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "배치 로그 한 줄을 분류한다. "
                    "로그에 없는 호스트명·고객 정보를 만들어 내지 않는다. "
                    "component를 모르겠으면 unknown. "
                    "타임아웃·429·5xx는 retryable=true 후보, "
                    "스키마/권한/잘못된 컬럼은 false 후보."
                ),
            },
            {"role": "user", "content": line},
        ],
        response_format=LogClassification,
    )
    msg = completion.choices[0].message
    if msg.refusal:
        raise RuntimeError(f"model refused: {msg.refusal}")
    if msg.parsed is None:
        raise RuntimeError("parsed result is None")
    return msg.parsed


def apply_policy(c):
    """Team policy on top of schema shape."""
    reason_l = c.reason.lower()
    if c.component == "csv-merge" and "invalid column" in reason_l:
        return c.model_copy(update={"retryable": False})
    return c
