#!/usr/bin/env python3
"""Print recurring visitor fingerprints from `knowledge/data/learning.sqlite` (local demo telemetry)."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Hammer demo learning stats")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repo root (folder containing wiki/). Default: inferred from this script location.",
    )
    parser.add_argument("--top", type=int, default=15, help="How many fingerprints to show")
    args = parser.parse_args()

    root = args.repo_root
    if root is None:
        root = Path(__file__).resolve().parents[2]
    root = Path(root).resolve()
    db = root / "knowledge" / "data" / "learning.sqlite"
    if not db.is_file():
        print(f"No learning DB at {db}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(db))
    try:
        rows = conn.execute(
            """
            SELECT fingerprint, COUNT(*) AS n, MAX(ts) AS last_ts
            FROM turns
            GROUP BY fingerprint
            ORDER BY n DESC
            LIMIT ?
            """,
            (max(1, args.top),),
        ).fetchall()
        details = []
        for fp, n, last_ts in rows:
            ex = conn.execute(
                "SELECT user_text FROM turns WHERE fingerprint = ? ORDER BY id DESC LIMIT 1",
                (fp,),
            ).fetchone()
            exemplar = ex[0] if ex else ""
            details.append((fp, n, last_ts, exemplar))
    finally:
        conn.close()

    print(f"repo_root={root}")
    print(f"learning_db={db}")
    print("---")
    for fp, n, last_ts, exemplar in details:
        ex = (exemplar or "").replace("\n", " ").strip()
        if len(ex) > 100:
            ex = ex[:97] + "…"
        print(f"{n:4d}  {fp}  last={last_ts}")
        print(f"      {ex}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
