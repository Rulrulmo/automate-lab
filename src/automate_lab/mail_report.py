"""Send a short batch summary over SMTP (Gmail app password friendly).

Blog: https://automate-lab.tistory.com/29
Stdlib only — never log SMTP_PASS.
"""
from __future__ import annotations

import argparse
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


def env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise RuntimeError(f"missing env: {name}")
    return v


def build_summary(ok: bool, title: str, lines: list[str]) -> tuple[str, str]:
    prefix = "[OK]" if ok else "[FAIL]"
    subject = f"{prefix} {title}"
    body = "\n".join(lines) + "\n"
    return subject, body


def send_mail(
    subject: str,
    body: str,
    attachments: list[Path] | None = None,
) -> None:
    host = env("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = env("SMTP_USER")
    password = env("SMTP_PASS")
    mail_from = os.environ.get("MAIL_FROM", user).strip() or user
    mail_to = [x.strip() for x in env("MAIL_TO").split(",") if x.strip()]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = mail_from
    msg["To"] = ", ".join(mail_to)
    msg.set_content(body)

    for path in attachments or []:
        data = path.read_bytes()
        if len(data) > 2_000_000:
            raise RuntimeError(f"attachment too large: {path}")
        maintype, subtype = "application", "octet-stream"
        if path.suffix.lower() == ".csv":
            maintype, subtype = "text", "csv"
        elif path.suffix.lower() == ".txt":
            maintype, subtype = "text", "plain"
        msg.add_attachment(
            data,
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send batch summary email")
    parser.add_argument("--fail", action="store_true", help="send [FAIL] demo")
    parser.add_argument("--attach", type=Path, action="append", default=[])
    args = parser.parse_args(argv)

    ok = not args.fail
    lines = [
        "job: nightly-csv-merge",
        f"status: {'success' if ok else 'failed'}",
        "files: 12",
        "rows: 3840",
        "out: /data/out/merged.csv",
    ]
    subject, body = build_summary(ok, "nightly CSV merge", lines)
    try:
        send_mail(subject, body, attachments=args.attach)
        print("mail sent")
        return 0
    except Exception as e:
        print(f"mail failed: {type(e).__name__}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
