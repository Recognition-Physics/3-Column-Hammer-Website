#!/usr/bin/env python3
"""Build / refresh the company knowledge SQLite DB from markdown (LLM Wiki layer).

Indexes the **voice-demo corpus** (allowlisted wiki pages + all `raw/hammer-data` markdown)
into kb_document, kb_chunk, and kb_chunk_fts for NotebookLM-style grounded retrieval.

Usage:
  python knowledge/scripts/sync_sqlite.py
  python knowledge/scripts/sync_sqlite.py --wiki-dir wiki --hammer-raw-dir raw/hammer-data
  python knowledge/scripts/sync_sqlite.py --full-wiki   # also index every page under wiki/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from knowledge.chunking import chunk_markdown, strip_frontmatter  # noqa: E402
from knowledge.retriever import ALLOWED_WIKI_FILES  # noqa: E402

DEFAULT_WIKI = REPO_ROOT / "wiki"
DEFAULT_HAMMER_RAW = REPO_ROOT / "raw" / "hammer-data"
DEFAULT_DB = REPO_ROOT / "knowledge" / "data" / "company_kb.sqlite"
SCHEMA_PATH = REPO_ROOT / "knowledge" / "schema.sql"
GENERATED_DIR = REPO_ROOT / "knowledge" / "generated"


def _first_heading_title(md: str) -> str | None:
    for line in md.splitlines():
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return None


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()


def _atomic_replace_db(final_path: Path, build_fn) -> None:
    final_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        suffix=".sqlite",
        prefix="company_kb_",
        dir=str(final_path.parent),
    )
    os.close(fd)
    tmp_path = Path(tmp_name)
    tmp_path.chmod(0o644)
    try:
        conn = sqlite3.connect(str(tmp_path))
        try:
            build_fn(conn)
            conn.commit()
        finally:
            conn.close()
        os.replace(tmp_path, final_path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def _insert_document(
    cur: sqlite3.Cursor,
    path_key: str,
    raw: str,
    kind: str,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    body = strip_frontmatter(raw)
    title = _first_heading_title(body) or Path(path_key).stem.replace("-", " ").title()
    digest = _sha256(body)
    cur.execute(
        """
        INSERT INTO kb_document (path, title, body, sha256, mtime_ns, kind)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (path_key, title, body, digest, 0, kind),
    )
    doc_id = int(cur.lastrowid)
    chunks = chunk_markdown(raw, max_chars=chunk_size, overlap=chunk_overlap)
    for idx, chunk in enumerate(chunks):
        cur.execute(
            "INSERT INTO kb_chunk (document_id, chunk_index, text) VALUES (?, ?, ?)",
            (doc_id, idx, chunk),
        )
    return len(chunks)


def sync(
    wiki_dir: Path,
    db_path: Path,
    *,
    hammer_raw_dir: Path | None,
    chunk_size: int,
    chunk_overlap: int,
    full_wiki: bool,
) -> dict[str, int]:
    if not wiki_dir.is_dir():
        raise SystemExit(f"Wiki directory not found: {wiki_dir}")

    stats = {"wiki_files": 0, "raw_files": 0, "files": 0, "chunks": 0}

    def build(conn: sqlite3.Connection) -> None:
        _init_schema(conn)
        cur = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()

        wiki_paths: list[Path] = []
        if full_wiki:
            wiki_paths = sorted(
                p
                for p in wiki_dir.rglob("*.md")
                if not any(part.startswith(".") for part in p.relative_to(wiki_dir).parts)
            )
        else:
            for name in ALLOWED_WIKI_FILES:
                p = wiki_dir / name
                if not p.is_file():
                    raise SystemExit(f"Missing allowlisted wiki file: {p}")
                wiki_paths.append(p)

        for path in wiki_paths:
            rel = path.relative_to(wiki_dir).as_posix() if full_wiki else path.name
            n = _insert_document(
                cur,
                rel,
                path.read_text(encoding="utf-8", errors="replace"),
                "wiki",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            stats["wiki_files"] += 1
            stats["files"] += 1
            stats["chunks"] += n

        if hammer_raw_dir and hammer_raw_dir.is_dir():
            root = hammer_raw_dir.resolve()
            for path in sorted(root.rglob("*.md")):
                if any(part.startswith(".") for part in path.relative_to(root).parts):
                    continue
                key = "raw/hammer-data/" + path.relative_to(root).as_posix()
                n = _insert_document(
                    cur,
                    key,
                    path.read_text(encoding="utf-8", errors="replace"),
                    "raw",
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
                stats["raw_files"] += 1
                stats["files"] += 1
                stats["chunks"] += n

        cur.execute(
            """
            INSERT INTO kb_sync (id, synced_at, wiki_root, file_count, chunk_count)
            VALUES (1, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              synced_at=excluded.synced_at,
              wiki_root=excluded.wiki_root,
              file_count=excluded.file_count,
              chunk_count=excluded.chunk_count
            """,
            (
                now,
                f"wiki={wiki_dir.resolve()}; raw={hammer_raw_dir.resolve() if hammer_raw_dir else 'none'}",
                stats["files"],
                stats["chunks"],
            ),
        )

        cur.execute("DELETE FROM kb_product")
        cur.executemany(
            """
            INSERT INTO kb_product (slug, name, summary, wiki_path, sort_order)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    "hammer-ai",
                    "Hammer AI",
                    "Dealership lead response, follow-up, and AI-assisted sales workflows (umbrella platform).",
                    "entity-hammer-ai.md",
                    10,
                ),
                (
                    "hammer-drive",
                    "Hammer Drive",
                    "Core AI sales agent: answers, qualifies, and books — agent (not chatbot) positioning per Hammer demo materials.",
                    "entity-hammer-ai.md",
                    20,
                ),
                (
                    "facebook-aia",
                    "Facebook AIA",
                    "Run sponsored Meta ads from live inventory and respond to every lead those ads generate.",
                    "entity-hammer-ai.md",
                    30,
                ),
                (
                    "marketposter",
                    "MarketPoster",
                    "Fills Marketplace via Chrome extension: listing site → select vehicles → Post → auto-fill details on Facebook (video transcript + MarketPoster PDF).",
                    "entity-hammer-ai.md",
                    40,
                ),
                (
                    "hammer-connect",
                    "Hammer Connect",
                    "Marketplace messaging: Marketplace threads route into Hammer; first reply via SMS alongside CRM queue (Hammer Connect PDF).",
                    "entity-hammer-ai.md",
                    50,
                ),
            ],
        )

    if db_path.exists():
        db_path.unlink()

    _atomic_replace_db(db_path, build)
    return stats


def write_coverage_md(
    db_path: Path,
    wiki_dir: Path,
    hammer_raw_dir: Path | None,
    stats: dict[str, int],
) -> Path:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    out = GENERATED_DIR / "db_coverage.md"
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT d.path, d.title, d.kind, COUNT(c.id) AS n_chunks
            FROM kb_document d
            LEFT JOIN kb_chunk c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.kind, d.path
            """
        ).fetchall()
        meta = conn.execute("SELECT * FROM kb_sync WHERE id = 1").fetchone()
    finally:
        conn.close()

    lines = [
        "# Knowledge base index (generated)",
        "",
        "_Auto-generated by `knowledge/scripts/sync_sqlite.py`. Do not edit by hand._",
        "",
        "## Sync",
        "",
        f"- **DB:** `{db_path.relative_to(REPO_ROOT).as_posix()}`",
        f"- **Wiki root:** `{wiki_dir.relative_to(REPO_ROOT).as_posix()}`",
        f"- **Hammer raw:** `{hammer_raw_dir.relative_to(REPO_ROOT).as_posix() if hammer_raw_dir else 'none'}`",
        f"- **Wiki files:** {stats.get('wiki_files', 0)}",
        f"- **Raw files:** {stats.get('raw_files', 0)}",
    ]
    if meta:
        lines.extend(
            [
                f"- **Synced at:** {meta['synced_at']}",
                f"- **Total files:** {meta['file_count']}",
                f"- **Chunks:** {meta['chunk_count']}",
            ]
        )
    lines.extend(["", "## Documents", "", "| Path | Kind | Title | Chunks |", "|------|------|-------|--------|"])
    for r in rows:
        lines.append(f"| `{r['path']}` | {r['kind']} | {r['title']} | {r['n_chunks']} |")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--wiki-dir", type=Path, default=DEFAULT_WIKI, help="Wiki folder")
    p.add_argument(
        "--hammer-raw-dir",
        type=Path,
        default=DEFAULT_HAMMER_RAW,
        help="Hammer markdown corpus (default: raw/hammer-data)",
    )
    p.add_argument("--db", type=Path, default=DEFAULT_DB, help="Output SQLite path")
    p.add_argument("--chunk-size", type=int, default=1200)
    p.add_argument("--chunk-overlap", type=int, default=150)
    p.add_argument(
        "--full-wiki",
        action="store_true",
        help="Index every wiki/*.md page (default: voice-demo allowlist only)",
    )
    p.add_argument("--json", action="store_true", help="Print machine-readable summary to stdout")
    args = p.parse_args()

    wiki_dir = args.wiki_dir.resolve()
    hammer_raw = args.hammer_raw_dir.resolve() if args.hammer_raw_dir else None
    db_path = args.db.resolve()

    stats = sync(
        wiki_dir,
        db_path,
        hammer_raw_dir=hammer_raw if hammer_raw and hammer_raw.is_dir() else None,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        full_wiki=args.full_wiki,
    )
    coverage = write_coverage_md(db_path, wiki_dir, hammer_raw, stats)

    if args.json:
        print(
            json.dumps(
                {
                    "wiki": str(wiki_dir),
                    "hammer_raw": str(hammer_raw) if hammer_raw else None,
                    "db": str(db_path),
                    **stats,
                    "coverage_md": str(coverage),
                }
            )
        )
    else:
        print(
            f"Indexed {stats['files']} files "
            f"({stats['wiki_files']} wiki, {stats['raw_files']} raw), "
            f"{stats['chunks']} chunks -> {db_path}"
        )
        print(f"Coverage: {coverage.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
