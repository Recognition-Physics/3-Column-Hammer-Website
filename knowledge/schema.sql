-- Company knowledge SQLite schema (LLM Wiki pattern + FTS search layer).
-- Rebuilt by scripts/sync_sqlite.py (idempotent full refresh).

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- Sync metadata (one row after each successful sync).
CREATE TABLE IF NOT EXISTS kb_sync (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  synced_at TEXT NOT NULL,
  wiki_root TEXT NOT NULL,
  file_count INTEGER NOT NULL,
  chunk_count INTEGER NOT NULL
);

-- One row per markdown page (wiki or mirrored raw summary).
CREATE TABLE IF NOT EXISTS kb_document (
  id INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  mtime_ns INTEGER,
  kind TEXT NOT NULL DEFAULT 'wiki' CHECK (kind IN ('wiki', 'raw'))
);

-- Optional structured products / offers (fill manually or via future importer).
CREATE TABLE IF NOT EXISTS kb_product (
  id INTEGER PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  summary TEXT,
  wiki_path TEXT,
  sort_order INTEGER NOT NULL DEFAULT 0
);

-- Chunked text for voice/RAG-style retrieval (BM25 via FTS5).
CREATE TABLE IF NOT EXISTS kb_chunk (
  id INTEGER PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES kb_document(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_kb_chunk_document ON kb_chunk(document_id);

CREATE VIRTUAL TABLE IF NOT EXISTS kb_chunk_fts USING fts5(
  text,
  content='kb_chunk',
  content_rowid='id',
  tokenize = "unicode61 remove_diacritics 2"
);

-- Keep FTS in sync with kb_chunk (external content FTS5).
CREATE TRIGGER IF NOT EXISTS kb_chunk_ai AFTER INSERT ON kb_chunk BEGIN
  INSERT INTO kb_chunk_fts(rowid, text) VALUES (new.id, new.text);
END;

CREATE TRIGGER IF NOT EXISTS kb_chunk_ad AFTER DELETE ON kb_chunk BEGIN
  INSERT INTO kb_chunk_fts(kb_chunk_fts, rowid, text) VALUES('delete', old.id, old.text);
END;

CREATE TRIGGER IF NOT EXISTS kb_chunk_au AFTER UPDATE ON kb_chunk BEGIN
  INSERT INTO kb_chunk_fts(kb_chunk_fts, rowid, text) VALUES('delete', old.id, old.text);
  INSERT INTO kb_chunk_fts(rowid, text) VALUES (new.id, new.text);
END;
