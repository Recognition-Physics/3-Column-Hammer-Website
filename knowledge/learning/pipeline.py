"""Log conversations and promote recurring themes into playbook markdown.

The assistant never edits its own system prompt. Learning appends markdown that retrieval indexes
(``playbook/approved.md`` and, when enabled, ``playbook/staging.md``). By default, promotions are
written to **approved.md** and the demo server clears its retriever cache so answers improve without a
manual merge or restart. Set ``HAMMER_LEARNING_AUTO_APPROVE=0`` to draft into **staging.md** only.
"""

from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

_PIPELINE_LOCK = threading.Lock()


def interaction_fingerprint(user_text: str) -> str:
    t = user_text.strip().lower()
    t = re.sub(r"\s+", " ", t)[:480]
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:20]


def _learning_db(repo_root: Path) -> Path:
    return (repo_root / "knowledge" / "data" / "learning.sqlite").resolve()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS turns (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts TEXT NOT NULL,
          channel TEXT NOT NULL,
          fingerprint TEXT NOT NULL,
          user_text TEXT NOT NULL,
          assistant_text TEXT NOT NULL,
          retrieval_best_score REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_turns_fp ON turns(fingerprint);

        CREATE TABLE IF NOT EXISTS promoted (
          fingerprint TEXT PRIMARY KEY,
          promoted_ts TEXT NOT NULL,
          target TEXT NOT NULL
        );
        """
    )
    conn.commit()


def _promotion_threshold() -> int:
    try:
        return max(2, min(50, int(os.environ.get("HAMMER_LEARNING_PROMOTE_AFTER", "5"))))
    except ValueError:
        return 5


def _auto_approve_enabled() -> bool:
    """When true (default), promoted sections append to approved.md and go live on next cache refresh.

    Set ``HAMMER_LEARNING_AUTO_APPROVE=0`` to append to staging.md instead (drafts). If staging
    indexing is on, those drafts still influence retrieval without editing approved.md.
    """

    raw = os.environ.get("HAMMER_LEARNING_AUTO_APPROVE", "1").strip().lower()
    return raw not in ("0", "false", "no")


def _min_user_chars() -> int:
    try:
        return max(8, min(200, int(os.environ.get("HAMMER_LEARNING_MIN_USER_CHARS", "18"))))
    except ValueError:
        return 18


def _fallback_playbook_block(exemplar: str, assistant_reply: str, hit_count: int) -> str:
    ex = exemplar.strip()
    if len(ex) > 300:
        ex = ex[:297].rstrip() + "…"
    ar = assistant_reply.strip()
    if len(ar) > 520:
        ar = ar[:517].rstrip() + "…"
    return (
        f"### Learned objection (auto · ×{hit_count} similar asks)\n\n"
        f"**Visitor theme:** Dealers often push back with wording like: “{ex}”\n\n"
        f"**Tyler-style reply hint (polish with a human — stay excerpt-grounded on facts):** {ar}\n\n"
        "_Facts and stats must still match EXCERPTS; use this block for angle and phrasing._\n"
    )


def _draft_via_openai(exemplar: str, assistant_reply: str) -> str | None:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    model = os.environ.get("HAMMER_LEARNING_DRAFT_MODEL", "gpt-4o-mini").strip()
    url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
    sys_msg = (
        "You maintain an internal Hammer AI sales playbook as markdown sections.\n"
        "Hammer sells dealership lead response AI (SMS, web chat, integrations).\n"
        "Output ONLY markdown — no preamble — matching this shape:\n"
        "### Learned objection: <short title>\n"
        "**Visitor theme:** one sentence paraphrasing the recurring pushback.\n"
        "**Tyler-style reply hint:** 2–4 short sentences, conversational, confident BDC tone.\n"
        "Rules: do NOT invent pricing, stats, integrations, or OEM facts. "
        "If specifics are uncertain, speak in general dealership framing only.\n"
        "Do not mention marketing collateral, PDFs, one-pagers, wikis, or internal docs — Tyler speaks from experience.\n"
        "Do not use bullet lists."
    )
    user_payload = (
        f"Recent visitor message:\n{exemplar[:1200]}\n\n"
        f"Assistant reply from the demo (may be imperfect):\n{assistant_reply[:1200]}\n"
    )
    try:
        import httpx

        r = httpx.post(
            url,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "temperature": 0.35,
                "messages": [
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": user_payload},
                ],
            },
            timeout=45.0,
        )
        r.raise_for_status()
        data = r.json()
        choices = data.get("choices") or []
        text = ((choices[0].get("message") or {}).get("content") or "").strip()
        return text if text else None
    except Exception:
        return None


def _read_playbook_corpora(repo_root: Path) -> tuple[str, str]:
    approved = repo_root / "knowledge" / "playbook" / "approved.md"
    staging = repo_root / "knowledge" / "playbook" / "staging.md"
    a_txt = approved.read_text(encoding="utf-8") if approved.is_file() else ""
    s_txt = staging.read_text(encoding="utf-8") if staging.is_file() else ""
    return a_txt, s_txt


def _already_covered(exemplar: str, approved_txt: str, staging_txt: str) -> bool:
    needle = exemplar.strip().lower()[:120]
    if len(needle) < _min_user_chars():
        return False
    blob = (approved_txt + "\n" + staging_txt).lower()
    return needle in blob


def _append_playbook_file(path: Path, block: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prev = path.read_text(encoding="utf-8") if path.is_file() else ""
    sep = "\n\n" if prev.strip() else ""
    path.write_text(prev.rstrip() + sep + block.strip() + "\n", encoding="utf-8")


def _maybe_promote(
    repo_root: Path,
    fingerprint: str,
    *,
    cache_clear: Callable[[], None] | None,
) -> None:
    threshold = _promotion_threshold()
    db_path = _learning_db(repo_root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    auto_approve = _auto_approve_enabled()
    promoted_to: str | None = None

    with _PIPELINE_LOCK:
        conn = sqlite3.connect(str(db_path))
        try:
            _ensure_schema(conn)
            total = conn.execute(
                "SELECT COUNT(*) FROM turns WHERE fingerprint = ?", (fingerprint,)
            ).fetchone()[0]
            if total < threshold:
                return

            row = conn.execute(
                "SELECT 1 FROM promoted WHERE fingerprint = ?", (fingerprint,)
            ).fetchone()
            if row:
                return

            ut_row = conn.execute(
                "SELECT user_text, assistant_text FROM turns WHERE fingerprint = ? ORDER BY id DESC LIMIT 1",
                (fingerprint,),
            ).fetchone()
            if not ut_row:
                return
            ut, at = ut_row

            approved_txt, staging_txt = _read_playbook_corpora(repo_root)
            if _already_covered(ut, approved_txt, staging_txt):
                conn.execute(
                    "INSERT OR REPLACE INTO promoted(fingerprint, promoted_ts, target) VALUES (?,?,?)",
                    (fingerprint, _utc_iso(), "skipped_duplicate"),
                )
                conn.commit()
                return

            drafted = _draft_via_openai(ut, at)
            block = drafted if drafted else _fallback_playbook_block(ut, at, total)
            if len(block) > 4000:
                block = block[:3997].rstrip() + "…"

            target = repo_root / "knowledge" / "playbook" / ("approved.md" if auto_approve else "staging.md")
            _append_playbook_file(target, block)
            promoted_to = target.name

            conn.execute(
                "INSERT INTO promoted(fingerprint, promoted_ts, target) VALUES (?,?,?)",
                (fingerprint, _utc_iso(), target.name),
            )
            conn.commit()
        finally:
            conn.close()

    if promoted_to is None:
        return
    if cache_clear:
        try:
            cache_clear()
        except Exception:
            pass
    print(
        f"[hammer-learning] promoted recurring theme fp={fingerprint} into {promoted_to}",
        flush=True,
    )


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record_turn_impl(
    repo_root: Path,
    *,
    channel: str,
    fingerprint: str,
    user_text: str,
    assistant_text: str,
    retrieval_best_score: float,
) -> None:
    db_path = _learning_db(repo_root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _PIPELINE_LOCK:
        conn = sqlite3.connect(str(db_path))
        try:
            _ensure_schema(conn)
            conn.execute(
                "INSERT INTO turns(ts, channel, fingerprint, user_text, assistant_text, retrieval_best_score) "
                "VALUES (?,?,?,?,?,?)",
                (_utc_iso(), channel, fingerprint, user_text, assistant_text, float(retrieval_best_score)),
            )
            conn.commit()
        finally:
            conn.close()


def _after_turn_worker(
    repo_root: Path,
    *,
    channel: str,
    user_text: str,
    assistant_text: str,
    retrieval_best_score: float,
    cache_clear: Callable[[], None] | None,
) -> None:
    try:
        ut = user_text.strip()
        at = assistant_text.strip()
        if len(ut) < _min_user_chars() or not at:
            return

        fp = interaction_fingerprint(ut)
        _record_turn_impl(
            repo_root,
            channel=channel,
            fingerprint=fp,
            user_text=ut,
            assistant_text=at,
            retrieval_best_score=retrieval_best_score,
        )
        _maybe_promote(repo_root, fp, cache_clear=cache_clear)
    except Exception as exc:  # pragma: no cover - demo resilience
        print(f"[hammer-learning] pipeline error: {exc}", flush=True)


def schedule_after_turn(
    repo_root: Path,
    *,
    user_text: str,
    assistant_text: str,
    retrieval_best_score: float,
    channel: str = "demo",
    cache_clear: Callable[[], None] | None = None,
) -> None:
    """Fire-and-forget: records the turn and may append playbook markdown."""

    if os.environ.get("HAMMER_LEARNING_ENABLED", "1").strip().lower() in ("0", "false", "no"):
        return

    root = Path(repo_root).resolve()

    def _run() -> None:
        _after_turn_worker(
            root,
            channel=channel,
            user_text=user_text,
            assistant_text=assistant_text,
            retrieval_best_score=retrieval_best_score,
            cache_clear=cache_clear,
        )

    threading.Thread(target=_run, daemon=True).start()


def after_turn(
    repo_root: Path,
    *,
    user_text: str,
    assistant_text: str,
    retrieval_best_score: float,
    channel: str = "demo",
    cache_clear: Callable[[], None] | None = None,
) -> None:
    """Backward-compatible alias for :func:`schedule_after_turn`."""

    schedule_after_turn(
        repo_root,
        user_text=user_text,
        assistant_text=assistant_text,
        retrieval_best_score=retrieval_best_score,
        channel=channel,
        cache_clear=cache_clear,
    )
