# HAMMERFINALSITE — Hammer production website

GitHub: **`Tyler-RecognitionPhysics/HAMMERFINALSITE`** · Vercel project: **`hammer-finalsite`**

This repo is the **production Hammer marketing + voice signup site** (replaces the public Hammer website when deployed).

## Go live in 5 steps

1. **Push this folder to GitHub** (or connect the repo you already use).
2. **Import in [Vercel](https://vercel.com)** → New Project → select the repo.  
   Vercel reads **`vercel.json`** at the repo root (build + API — do not change paths unless you know why).
3. **Add secrets in Vercel** → Project → **Settings** → **Environment Variables** (Production).  
   Copy names from **`demo/realtime-sales-demo/server/.env.example`** — full checklist in **`GO-LIVE-VERCEL.md`**.
4. **Set up Zapier** (agreement email + “I approve”) — guides in **`demo/realtime-sales-demo/server/zapier/README.md`**.
5. **Deploy**, then open your domain → **Start call** and run one test signup.

Detailed checklist: **[GO-LIVE-VERCEL.md](./GO-LIVE-VERCEL.md)**

---

## Folder map (what each top-level folder is)

| Folder | Plain English name | You need it for go-live? |
|--------|-------------------|---------------------------|
| **`api/`** | Vercel server hook (runs the Python API in the cloud) | Yes — do not delete |
| **`demo/realtime-sales-demo/`** | **The actual website** (browser UI + Python backend) | Yes — this is the app |
| **`vercel.json`** | Vercel build + routing config | Yes — do not delete |
| **`wiki/`** | Website text + AI knowledge (marketing copy) | Yes — bundled on deploy |
| **`knowledge/`** | Search index (SQLite) for the voice AI | Yes — built/bundled on deploy |
| **`raw/hammer-data/`** | Extra Hammer PDFs/transcripts for AI answers | Optional but recommended |
| **`scripts/`** | Helper scripts (e.g. push API key to Vercel) | Optional |
| **`.cursor/`** | Cursor editor settings | Ignore for deploy |

---

## Run on your computer (before Vercel)

From **`demo/realtime-sales-demo/`**:

| Script | What it does |
|--------|----------------|
| **`1-START-LOCAL-API.ps1`** | Starts the Python API on port **8780** |
| **`2-START-LOCAL-WEB.ps1`** | Starts the browser UI on port **5173** |
| **`run-demo.ps1`** | Same as (1) — old name kept for compatibility |

1. Copy **`demo/realtime-sales-demo/server/.env.example`** → **`server/.env`** and fill in secrets.  
2. Run **`1-START-LOCAL-API.ps1`**, then **`2-START-LOCAL-WEB.ps1`**.  
3. Open **http://127.0.0.1:5173**

More detail: **`demo/realtime-sales-demo/README.md`**

---

## Where secrets live (never in the browser)

| Location | Safe? |
|----------|--------|
| **`server/.env`** (local only, gitignored) | Yes — local dev |
| **Vercel Environment Variables** | Yes — production |
| **`web/` `VITE_*` variables** | Public in JS — **never put API keys here** |

OpenAI keys are used **only on the server**; the browser gets short-lived tokens from `/api/realtime/session`.
