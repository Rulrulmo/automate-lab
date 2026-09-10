"""Merge PDFs in an explicit order with pypdf.

Blog: https://automate-lab.tistory.com/26
"""
from __future__ import annotations

import argparse
from pathlib import Path


def merge_in_order(
    src: Path,
    names: list[str],
    out: Path,
    *,
    dry: bool = False,
) -> list[str]:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise ImportError("pypdf required: pip install 'automate-lab[pdf]'") from exc

    writer = PdfWriter()
    log: list[str] = []

    for name in names:
        path = src / name
        if not path.exists():
            log.append(f"MISSING {name}")
            continue
        try:
            reader = PdfReader(str(path))
        except Exception as e:
            log.append(f"FAIL {name} ({type(e).__name__}: {e})")
            continue

        if getattr(reader, "is_encrypted", False):
            log.append(f"SKIP encrypted {name}")
            continue
        if len(reader.pages) == 0:
            log.append(f"SKIP empty {name}")
            continue

        log.append(f"{'PLAN' if dry else 'OK'} {name} pages={len(reader.pages)}")
        if dry:
            continue
        for page in reader.pages:
            writer.add_page(page)

    if dry:
        log.append("dry-run only, no file written")
        return log

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as f:
        writer.write(f)
    log.append(f"wrote {out} total_pages={len(writer.pages)}")
    return log


def list_pdf_names(src: Path) -> list[str]:
    files = [p for p in src.iterdir() if p.suffix.lower() == ".pdf" and p.is_file()]
    return [p.name for p in sorted(files, key=lambda p: p.name.lower())]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge PDFs in order")
    parser.add_argument("--src", type=Path, default=Path("inbox_pdfs"))
    parser.add_argument("--out", type=Path, default=Path("out/merged.pdf"))
    parser.add_argument("--order", type=str, default="", help="comma-separated filenames")
    parser.add_argument("--order-file", type=Path, help="one filename per line")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    src = args.src.expanduser()
    if not src.is_dir():
        raise SystemExit(f"src not found: {src}")

    if args.order_file:
        names = [
            line.strip()
            for line in args.order_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
    elif args.order.strip():
        names = [n.strip() for n in args.order.split(",") if n.strip()]
    else:
        names = list_pdf_names(src)

    for line in merge_in_order(src, names, args.out.expanduser(), dry=args.dry_run):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
