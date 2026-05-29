#!/usr/bin/env python3
"""Extract a PDF to markdown for the hammer-data corpus."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Install pypdf: py -3 -m pip install pypdf", file=sys.stderr)
    raise


def pdf_to_markdown(pdf_path: Path, title: str | None = None) -> str:
    reader = PdfReader(str(pdf_path))
    doc_title = title or pdf_path.stem
    lines = [f"# {doc_title}", ""]

    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        text = text.replace("\uFFFD", "'")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        if not blocks:
            blocks = [text]
        for block in blocks:
            if len(block) < 100 and (block.endswith("?") or block.isupper()):
                lines.append(f"## {block}")
            else:
                lines.append(block)
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf", type=Path, help="Source PDF path")
    p.add_argument("-o", "--output", type=Path, help="Output .md path (default: <pdf>.md)")
    args = p.parse_args()

    pdf = args.pdf.resolve()
    if not pdf.is_file():
        raise SystemExit(f"PDF not found: {pdf}")

    out = args.output.resolve() if args.output else pdf.with_suffix(pdf.suffix + ".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    md = pdf_to_markdown(pdf, title=f"{pdf.stem}.pdf")
    out.write_text(md, encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
