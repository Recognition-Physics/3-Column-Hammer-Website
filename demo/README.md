# demo/ — main website app lives here

## The live site

Everything you need is in:

### **`realtime-sales-demo/`** ← Hammer voice website (UI + API)

| Subfolder | Plain English |
|-----------|----------------|
| **`web/`** | Public website (HTML, CSS, voice UI) — built by Vercel |
| **`server/`** | Private API (OpenAI, Zapier, Hammer Office) — secrets go in `server/.env` |
| **`1-START-LOCAL-API.ps1`** | Run API locally |
| **`2-START-LOCAL-WEB.ps1`** | Run browser UI locally |

Start here for local dev or deep docs: **`realtime-sales-demo/README.md`**

## Other

| Path | Purpose |
|------|---------|
| **`shared/site_copy.py`** | Loads marketing copy from `wiki/` for the API |

Other folders under `demo/` (if any) are not used for this production deploy.
