# Hammer voice website (main app)

> **Repo root:** see **`../../README.md`** (folder map) and **`../../GO-LIVE-VERCEL.md`** (deploy checklist).

One-page voice signup site using **OpenAI `gpt-realtime-2`** (WebRTC in the browser) and **wiki + Hammer markdown–grounded** `search_wiki` tool calls to the FastAPI backend.

## Quick start (local)

| Step | Command |
|------|---------|
| 1 | Copy `server/.env.example` → `server/.env` and add secrets |
| 2 | `.\1-START-LOCAL-API.ps1` |
| 3 | `.\2-START-LOCAL-WEB.ps1` (second terminal) |
| 4 | Open **http://127.0.0.1:5173** |

Folders: **`web/`** = public UI · **`server/`** = private API · **`server/zapier/`** = email setup guides

## Prerequisites

- **Python 3.10+** with `pip`
- **Node 18+** and `npm`
- **This repo’s `wiki/` tree** (allowlisted files used by `server/wiki_retrieval.py`)
- **`raw/hammer-data/**/*.md`** when present (same retriever; optional via env)
- **OpenAI API key** with Realtime access, set on the machine running the API:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

## Run (development — two terminals)

**Terminal A — API (port 8780):**

```powershell
cd demo\realtime-sales-demo\server
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app:app --host 127.0.0.1 --port 8780 --reload --reload-include .env
```

**Terminal B — Vite (port 5173, proxies `/api` → 8780):**

```powershell
cd demo\realtime-sales-demo\web
npm install
npm run dev
```

Open **http://127.0.0.1:5173** in Chrome or Edge. Allow microphone access, then **Start call**.

## Run (single server after build)

```powershell
cd demo\realtime-sales-demo\web
npm run build
cd ..\server
py -3 -m uvicorn app:app --host 127.0.0.1 --port 8780
```

Then open **http://127.0.0.1:8780/** (API serves the Vite `dist/` folder).

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | (required) | Mint ephemeral client secrets |
| `REALTIME_SALES_MODEL` | `gpt-realtime-2` | Realtime model id |
| `REALTIME_SALES_WIKI_DIR` | `<repo>/wiki` | Wiki root for BM25 retrieval |
| `REALTIME_SALES_INCLUDE_HAMMER_RAW` | `1` | Set `0` to index wiki only (skip `raw/hammer-data/`) |
| `REALTIME_SALES_HAMMER_RAW_DIR` | `<repo>/raw/hammer-data` | Override path to the Hammer markdown tree |
| `REALTIME_SALES_CORS_ORIGINS` | `http://127.0.0.1:5173,...` | CORS for dev |
| `REALTIME_SALES_TOP_K` | `8` | Grounded chunks returned to the tool (max 12) |
| `REALTIME_SALES_KB_DB` | `<repo>/knowledge/data/company_kb.sqlite` | SQLite FTS index used by retrieval |
| `ZAPIER_LEAD_WEBHOOK_URL` | (required for voice signup) | Voice AI Catch Hook — agreement email (Zap 1) |
| `ZAPIER_WEBSITE_LEAD_WEBHOOK_URL` | (required for website form) | Separate Catch Hook for “Get started” modal only |
| `ZAPIER_APPROVAL_CALLBACK_SECRET` | (recommended) | Shared secret; Zap 2 POSTs `X-Zapier-Secret` to `/api/zapier/approval` |

### Zapier setup (agreement email + “I approve”)

**Zap 1 — Send agreement on voice signup** (`ZAPIER_LEAD_WEBHOOK_URL` only — not the website form)

1. Trigger: **Webhooks by Zapier** → **Catch Hook** → copy URL into `ZAPIER_LEAD_WEBHOOK_URL`.
2. Filter: `event` **equals** `agreement_email_request`.
3. Action: **Gmail** → **Send Email**  
   - Filter (add): `productLine` equals `hammer_drive` (Hammer Drive) or `facebook_aia` (Facebook AIA). See `server/zapier/HAMMER_DRIVE_EMAIL.md` and `server/zapier/FACEBOOK_AIA_EMAIL.md`.  
   - **To:** `email`  
   - **Subject:** `agreementEmailSubject`  
   - **Body:** `agreementEmailHtml` (HTML with HAMMER AI logo banner — set Gmail to **HTML** mode), or plain `agreementEmailBody`.  
   - Or build your own body using `dealershipName`, `subscriptionMonthlyDisplay`, `firstMonthBillingDisplay`, `nextPaymentDate`, `billingSummary`.  
   - See `server/zapier/HAMMER_DRIVE_EMAIL.md`.

**Zap 2 — Record “I approve” (required before account creation)**

The voice agent calls `check_agreement_approval` which reads this callback. **Without Zap 2, the AI cannot verify email approval.**

Full setup: [`server/zapier/ZAPIER_I_APPROVE_SETUP.md`](server/zapier/ZAPIER_I_APPROVE_SETUP.md)

1. Trigger: **Gmail** → **New Email** (inbox that receives agreement replies).
2. Filter: body **contains** `I approve`.
3. Action: **Webhooks by Zapier** → **POST**  
   - URL: `https://<your-host>/api/zapier/approval` (local: `http://127.0.0.1:8780/api/zapier/approval`)  
   - Header: `X-Zapier-Secret: <ZAPIER_APPROVAL_CALLBACK_SECRET>`  
   - JSON: `{ "email": "<sender email>", "approved": true, "reply_text": "<body plain>" }`  
4. Optional: send password email, Slack notify, etc.

**API**

| Route | Purpose |
|-------|---------|
| `POST /api/lead` | Voice → `ZAPIER_LEAD_WEBHOOK_URL`; website form → `ZAPIER_WEBSITE_LEAD_WEBHOOK_URL` |
| `POST /api/zapier/approval` | Zap 2 callback when visitor approves |
| `GET /api/zapier/approval-status?email=` | Voice tool `check_agreement_approval` |
| `POST /api/hammer/create-account` | Voice tool `create_hammer_account` (PHASE B, after I approve) |

Voice signup sends `channel: voice` and `event: agreement_email_request` to **`ZAPIER_LEAD_WEBHOOK_URL`**. The website lead modal sends `channel: website` (`event: website_lead`) to **`ZAPIER_WEBSITE_LEAD_WEBHOOK_URL`** — a separate Zap / Catch Hook.

**Website form Zap** — create a new Catch Hook (do not reuse Zap 1):

1. Trigger: **Webhooks by Zapier** → **Catch Hook** → `ZAPIER_WEBSITE_LEAD_WEBHOOK_URL`.
2. Map fields such as `responseId`, `createTime`, `firstName`, `notes`, `email`, `phoneNumber`, `leadSource` (`website form`).
3. No filter on `agreement_email_request` required — this hook only receives `website_lead` events.

### Hammer Office account creation (PHASE B)

After Zap 2 records **I approve**, the voice agent collects name, phone, website, and role, then calls **`create_hammer_account`**. The server logs into [Hammer Office](https://office.hammer-corp.com/accounts/new) with staff credentials and submits the new-account form.

Set on the server (see `server/.env.example`):

| Variable | Purpose |
|----------|---------|
| `HAMMER_OFFICE_EMAIL` | Staff login for office.hammer-corp.com |
| `HAMMER_OFFICE_PASSWORD` | Staff password |
| `HAMMER_OFFICE_DRY_RUN=1` | Fill form only — do not submit (local testing) |
| `HAMMER_OFFICE_USE_PLAYWRIGHT=1` | Browser automation if httpx form POST fails |
| `HAMMER_OFFICE_HEADLESS=0` | Visible Chromium window while creating accounts |
| `HAMMER_OFFICE_SLOW_MO=400` | Slow down actions (ms) when watching the browser |
| `HAMMER_OFFICE_KEEP_OPEN=120` | Seconds to keep the window open after submit |

The endpoint rejects creation until `GET /api/zapier/approval-status` shows **approved** for the buyer email.

## Voice vs Platform playground (`gpt-realtime-2`)

OpenAI does **not** guarantee identical spoken output between your browser session and the **Platform playground**, even on the same model id. Perceived voice quality depends on the selected **voice** preset, **`audio.output.speed`**, **semantic VAD** timing, **instructions / persona** (sales prompting changes rhythm and phrasing), and **playback hardware** (Bluetooth vs wired, laptop speakers, and so on).

**Voice:** browser and server WebRTC/SIP use a **locked** voice (`shimmer`, speed `1.0`) via `web/src/realtime-voice.ts` and `server/realtime_voice_config.py` — `VITE_REALTIME_VOICE` / `REALTIME_SALES_VOICE` env vars are **not** used (prevents a different voice on each reconnect). Judge on **wired headphones** when possible, and use **`VITE_REALTIME_PLAYGROUND_PARITY`** (below) to A/B a neutral assistant prompt vs the full Hammer sales instructions.

### Recommended web `.env` (parity baseline)

Create `demo/realtime-sales-demo/web/.env`:

```bash
# Voice is locked to shimmer in code — no VITE_REALTIME_VOICE needed.
# 1 / true / yes = minimal prompt + softer VAD + no wiki tools (see table).
VITE_REALTIME_PLAYGROUND_PARITY=0
```

### Web client (`Vite`) variables

| Variable | Default | Purpose |
|----------|---------|---------|
| *(voice)* | `shimmer` @ `1.0` (locked in code) | `audio.output.voice` — not env-configurable |
| *(voice speed)* | `1` (locked in code) | `audio.output.speed` |
| `VITE_REALTIME_PLAYGROUND_PARITY` | (unset / falsy) | When truthy: neutral minimal instructions, `semantic_vad` **eagerness `medium`**, omit `reasoning.effort`, empty tools (no `search_wiki`) — isolates persona/tool cadence vs production Hammer prompting |
| `VITE_SIGN_IN_URL` | Hammer dashboard URL | Sign-in destination link |
| `VITE_ELEVENLABS_TOKEN_PREFETCH` | enabled | Prefetches the ElevenLabs browser conversation token on strong intent (hover/focus/pointerdown) to reduce first-click latency; set `0` to disable. |
| `VITE_VOICE_LATENCY_DEBUG` | disabled | Logs browser voice timing marks (`token_ready_for_start`, `webrtc_on_connect`, `first_speaking`) to the console. |

### Agents SDK version

The web client uses **`@openai/agents` ^0.11.x** (requires **`zod` ^4** as a peer dependency). Upgrading from older 0.2.x lines aligns with current Realtime session tooling in the SDK; see [openai-agents-js releases](https://github.com/openai/openai-agents-js/releases) for incremental fixes affecting realtime or audio.

## HTTPS note

Browsers require a **secure context** for microphone access. `localhost` / `127.0.0.1` work over HTTP; public deploys should use **HTTPS**.

## Deploy on Vercel (frontend + voice API)

Repo-root `vercel.json` deploys:

- **Static UI** — Vite build from `demo/realtime-sales-demo/web/` → `dist/`
- **Voice / chat API** — Python serverless `api/index.py` (FastAPI via Mangum) for `/api/*`

**Vercel project settings**

1. Import the GitHub repo.
2. **Root Directory:** leave **empty** (must include repo-root `api/` and `vercel.json`). Do **not** set Root Directory to `web/` only — the API will not deploy.
3. Clear any **Output Directory** override in Settings.
4. **Environment variables** (Project → Settings → Environment Variables):

| Variable | Required | Notes |
|----------|----------|--------|
| `OPENAI_API_KEY` | **Yes** | Realtime session + chat. Without it, **Start call** fails with HTTP 503. |
| `REALTIME_SALES_CORS_ORIGINS` | Optional | Extra origins (comma-separated). Vercel preview/production URLs are added automatically. |

   From a machine with `server/.env` and a [Vercel token](https://vercel.com/account/tokens):

   ```powershell
   $env:VERCEL_TOKEN = "..."
   .\scripts\push-openai-key-to-vercel.ps1 -ProjectName sellmeapen
   ```

5. **Redeploy** after env changes (required — env vars are not applied to old deployments).

**Build log check:** `vite build` + Python `api/index.py` bundled. Open `https://<your-deployment>/api/health` — should show `"ok": true` and **`"openai_configured": true`**.

**Start call** uses `POST /api/realtime/session` on the same host (no separate API URL in the browser).

**Limits:** Serverless cold starts can add a few seconds before the first wiki search; learning pipeline is disabled on Vercel (`HAMMER_LEARNING_ENABLED=0`).
