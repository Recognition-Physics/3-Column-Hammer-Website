# raw/ — source documents for the AI

## `hammer-data/`

PDFs and transcripts converted to **`.md`** files. The voice agent searches these (with `wiki/`) so answers stay grounded in real Hammer material.

- **Go-live:** Included automatically on Vercel (`vercel.json` bundles `raw/hammer-data/**`).
- **Optional:** Set `REALTIME_SALES_INCLUDE_HAMMER_RAW=0` on the server to use wiki only.

Do not store secrets here — only marketing/sales content.
