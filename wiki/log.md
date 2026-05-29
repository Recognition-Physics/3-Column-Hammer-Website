# Wiki log

Append-only timeline for this knowledge base. Suggested entry format:

`## [YYYY-MM-DD] type | Short title`

---

## [2026-05-14] bootstrap | LLM Wiki scaffold

Initialized the LLM Wiki layout for this repo: `raw/`, `wiki/` (index, overview, concept seeds, pattern reference), and `AGENTS.md` maintainer schema. Content seeded from existing repository README and structure; no new external sources ingested.

## [2026-05-14] ingest | Hammer Data

Copied 18 markdown files from `C:\Users\tbenn\Downloads\Hammer Data` to `raw/hammer-data/` (includes `Hammer Website/` subfolder). Redacted spoken payment-card segment in `Hammer_Sales_Renewal_and_Dealer_Trial_Activation.md` before retaining in git. Added wiki pages [source-hammer-data.md](source-hammer-data.md) and [entity-hammer-ai.md](entity-hammer-ai.md); updated [index.md](index.md).

## [2026-05-14] feature | Voice demo canonical wiki

Added [company-voice-demo-canonical.md](company-voice-demo-canonical.md) as the allowlisted corpus pointer for the browser Hammer voice assistant demo; updated [index.md](index.md).

## [2026-05-15] ingest | Hammer Data (resync)

Re-copied all files from `C:\Users\tbenn\Downloads\Hammer Data` into `raw/hammer-data/` (18 markdown files; PDF-exports under `Hammer Website/` mapped to the existing subfolder). Added repeatable script [ingest-from-downloads.ps1](../raw/hammer-data/ingest-from-downloads.ps1). Updated provenance in [source-hammer-data.md](source-hammer-data.md).

**Note:** If Windows shows `WATCH_..._??.md` in Downloads, that is the same video companion doc as `WATCH_..._🚗.md`; the copy may use the Downloads filename. Prefer the emoji filename for clarity when renaming manually.

## [2026-05-16] ingest | Hammer Website PDF markdown

Re-ran [`ingest-from-downloads.ps1`](../raw/hammer-data/ingest-from-downloads.ps1) with source `C:\Users\tbenn\Downloads\Hammer Data` (full bundle overwrite). Confirmed the five PDF-derived files under `raw/hammer-data/Hammer Website/` (Facebook AIA, lead follow-up ×2, Connect, MarketPoster). Expanded per-file manifest rows in [source-hammer-data.md](source-hammer-data.md).

## [2026-05-17] ingest | AIA Guide PDF

Extracted `C:\Users\tbenn\Downloads\AIA Guide (4).pdf` to [AIA Guide (4).pdf.md](../raw/hammer-data/AIA%20Guide%20(4).pdf.md) via [pdf_to_md.py](../raw/hammer-data/scripts/pdf_to_md.py). Updated manifest in [source-hammer-data.md](source-hammer-data.md) and AIA details in [entity-hammer-ai.md](entity-hammer-ai.md). Rebuilt SQLite KB (`knowledge/scripts/sync_sqlite.py`).

## [2026-05-17] feature | Wiki-sourced demo site copy

Added [demo-public-site-copy.md](demo-public-site-copy.md) as the single source for browser UI strings on both voice demos. Both backends expose `GET /api/site_copy`; frontends load headlines, labels, and chips from this page only.

## [2026-05-17] feature | Realtime demo UI: validation → resolution

Restructured the realtime sales demo page around a **validate then resolve** narrative: journey rail, two-column evidence + voice lane, editorial typography (Bricolage Grotesque + Newsreader), and dark resolution strip. Copy updates live in [demo-public-site-copy.md](demo-public-site-copy.md).

## [2026-05-17] ingest | Deal-closed sales call (redacted)

Ingested `C:\Users\tbenn\Downloads\Hammer Sales Pitch with Deal CLosed.md` as repository-safe **[Hammer_Sales_Pitch_Call_Deal_Closed_Redacted.md](../raw/hammer-data/Hammer_Sales_Pitch_Call_Deal_Closed_Redacted.md)** (stripped **payment-card fields, EIN, phone numbers, and email text**). Updated commercial + dashboard notes in [entity-hammer-ai.md](entity-hammer-ai.md), manifest in [source-hammer-data.md](source-hammer-data.md), and rebuilt SQLite (`python knowledge/scripts/sync_sqlite.py`).

## [2026-05-18] copy | Nav panel How: feature titles

Added headline + body keys (`rt_nav_panel_how_2_title` … `rt_nav_panel_how_6_title`) in [demo-public-site-copy.md](demo-public-site-copy.md) and `<h4 class="nav-panel__feature-h">` in the realtime landing nav panel; bodies split from prior combined lines for clearer benefit-led scanning.

## [2026-05-19] positioning | Hammer north star (voice demos)

Documented demo synthesis in [entity-hammer-ai.md](entity-hammer-ai.md) (**North star — strategic outcome**), a short positioning spine pointer in [company-voice-demo-canonical.md](company-voice-demo-canonical.md), and aligned prompts: [demo/voice-assistant/llm_client.py](../demo/voice-assistant/llm_client.py) (`<role>`, sales framework, `WHAT HAMMER ACTUALLY DOES`, key phrases), [demo/realtime-sales-demo/server/sales_chat.py](../demo/realtime-sales-demo/server/sales_chat.py) (`TEXT_SALES_SYSTEM`), and realtime `BASE_INSTRUCTIONS` Step 4 in the web client. Added BM25 query expansions in [`knowledge/retriever.py`](../knowledge/retriever.py) for queries about shoppers comparing rooftops and yield on purchased leads.

## [2026-05-15] policy | Demo site name and phone capture

Updated [company-voice-demo-canonical.md](company-voice-demo-canonical.md) with demo behavior: when a browser voice visitor is engaged, Tyler should naturally collect **name + SMS-capable phone** for reconnect and follow-up text if the session drops; guardrails on cadence, opt-out, and no card collection. Wired the same priority into [demo/voice-assistant/llm_client.py](../demo/voice-assistant/llm_client.py) (`SYSTEM_PROMPT`: `<site_visitor_contact_capture>` plus response-length exception).
