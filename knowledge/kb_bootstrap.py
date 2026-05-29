"""Ensure the SQLite knowledge index exists before voice demos start."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = KNOWLEDGE_DIR.parent
DEFAULT_DB = KNOWLEDGE_DIR / "data" / "company_kb.sqlite"
SYNC_SCRIPT = KNOWLEDGE_DIR / "scripts" / "sync_sqlite.py"


def ensure_kb_database(
    repo_root: Path | None = None,
    *,
    db_path: Path | None = None,
    force: bool = False,
) -> Path:
    """Build `knowledge/data/company_kb.sqlite` when missing (or when `force=True`)."""
    root = (repo_root or REPO_ROOT).resolve()
    db = (db_path or (root / "knowledge" / "data" / "company_kb.sqlite")).resolve()
    if db.is_file() and not force:
        return db
    script = root / "knowledge" / "scripts" / "sync_sqlite.py"
    if not script.is_file():
        return db
    subprocess.run(
        [sys.executable, str(script), "--db", str(db)],
        cwd=str(root),
        check=False,
    )
    return db
