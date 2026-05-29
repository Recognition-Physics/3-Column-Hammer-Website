# Entity: Hammer (dealership AI / lead automation)

**Domain:** Automotive retail — AI-assisted internet lead response, SMS-first engagement, and long-horizon follow-up. **Not** part of the VibeVoice codebase; captured here from ingested marketing and call transcripts.

**Public surfaces (from sources):** [hammertime.com](https://www.hammertime.com/), dashboard/login references to `hammer-corp.com`.

## Hammer product names (use these in conversation)

When referring to Hammer’s **product modules** or SKUs (not generic “AI”), use these names from marketing / PDF sources in `raw/hammer-data/`:

| Name | What it is (short) |
|------|---------------------|
| **Hammer Drive** | Core dealership AI sales agent — answers, qualifies, and books; positioned as an **agent**, not a passive chatbot (see Hammer demo deck). **Includes website web chat** — Hammer places **webchat on the dealer’s website** as part of Hammer Drive (same agent thread as SMS/lead follow-up, not a separate SKU). **Craigslist vehicle postings** can be **ordered through Hammer** as part of Hammer Drive; **each post is $5.99** (Craigslist has **no free postings** — see pricing). **Posting cadence is fully customizable** — dealers decide **how often** and **when** (e.g. **every day**, **every other day**, lighter rotations, specific days/times); Hammer executes **their** schedule, **not** a one-size-fits-all vendor default. Spending scales with postings because **every listing is still $5.99**. Hammer **responds to Craigslist leads** the same way as any other inbound lead channel. |
| **Facebook AIA** | **A**utomotive **I**nventory **A**ds on **Meta** — Hammer **runs sponsored ads** from live inventory so vehicles appear **across both Facebook and Instagram** (carousel up to 25 units, auto-rotates) and **responds to every lead** (Facebook message → Hammer → CRM). See [AIA Guide (4).pdf.md](../raw/hammer-data/AIA%20Guide%20(4).pdf.md) and Facebook AIA PDF. |
| **MarketPoster** | **Chrome extension** on your **listing site** (where inventory is shown): pick **one vehicle or many** with checkboxes, click **Post**, and MarketPoster **auto-fills Facebook Marketplace** listings with vehicle details — pitched as **saving time** and getting **leads faster on Facebook** (short video demo transcript + [MarketPoster_Chrome_extension_video_demo_transcript.md](../raw/hammer-data/MarketPoster_Chrome_extension_video_demo_transcript.md); see also MarketPoster PDF in `raw/hammer-data/Hammer Website/`). **Hammer Connect** (Marketplace messaging into Hammer) is **included with MarketPoster at no additional charge** — not billed as a separate add-on. |
| **Hammer Connect** | **Marketplace messaging** — Marketplace threads land in Hammer next to SMS/CRM; shopper messages on Marketplace, Hammer routes and sends the **first text** back in the SMS channel (see Hammer Connect PDF). **Bundled in MarketPoster** at **no extra fee**. If a dealer wants **only** Hammer Connect **without** MarketPoster: **$199/month** standalone. |

These sit under the broader **Hammer AI** dealership platform; do not invent additional named products beyond what the wiki or `raw/` sources support.

## North star — strategic outcome (voice demo synthesis)

Hammer exists so dealers **squeeze more value from leads they already pay for** — not generic “better marketing.” Synthesized framing for demos (pair with excerpts and metrics elsewhere on this page; **not** new operational guarantees):

1. **Keep shoppers from drifting to other rooftops:** Internet leads surface in environments where competitors and alternate inventory are **one tap away**. Hammer’s instant SMS engagement (often while they still have your listing open) plus persistent follow-up is positioned to **keep your dealership first in the thread** instead of losing them while they shop around.

2. **Yield on sunk lead spend:** Providers charge **per name / per phone** — those touches are **already purchased**. Hammer focuses on **conversion and continuity**: first contact in seconds (including after-hours) and long-horizon follow-up so paid contacts don’t die after one or two attempts.

## What the product does

- **Instant engagement:** Text (and email where no phone) shortly after lead ingestion; positioning emphasizes speed while the shopper still has the listing open.
- **Website web chat (Hammer Drive):** Hammer **puts webchat on the dealership website** — included **in Hammer Drive**, not sold as a separate product. Shoppers who start on the site are handled by the same AI engagement model alongside third-party and SMS leads.
- **Craigslist postings (Hammer Drive):** Hammer **orders and posts vehicles to Craigslist** for dealers as part of **Hammer Drive** — the **capability is included** in the subscription (not a separate SKU), but **each Craigslist listing costs $5.99 per post**. There are **no free Craigslist postings**; never imply unlimited free posts. Always make the **$5.99 per post** fee explicit when Craigslist comes up. **Posting frequency is fully up to the dealership** — **fully customizable**: they choose **how often** and **which days/times** (e.g. **daily**, **every other day**, once a week, weekday-only, etc.); Hammer runs **their** cadence rather than imposing a mandatory schedule. Practical limit is appetite and budget, since **each post bills at $5.99**. Hammer **replies to Craigslist leads** like any other lead source (same AI engagement, CRM logging, and follow-up).
- **Persistent follow-up:** Automated re-touch after no-reply; nurtures 30–90+ day horizons when buyers self-report future timing. Transcripts cite **~51% “revival”** on leads otherwise marked cold/dead (verify with vendor; single-call claim).
- **CRM-native:** Pushes conversation summaries, next actions, sentiment, and links into existing CRM notes; does not replace CRM routing (round-robin / first-come preserved per sources).
- **Human + AI handoff:** When a salesperson sends a message, **immediate auto-replies** can pause so the human owns the thread; **long-term follow-up** may still run in parallel (per sales narrative).
- **Customization:** Tone, verbosity, dealership rules (e.g. price negotiation scripting), optional **human-like typing delay**, multilingual replies (French/Spanish/etc. cited in demos).
- **Inventory-aware replies:** Example flow: vague shopper request (“small, cute, good on gas”) → model suggests vehicles from dealer inventory with links and appointment push.
- **Meta ads (Facebook AIA):** Live inventory becomes **sponsored placements across both Facebook and Instagram** — dealers' vehicles show **on both Meta apps**, not Facebook alone; Hammer **runs the campaigns** and **answers every lead** those ads produce — not just the ad placement (see Facebook AIA PDF in `raw/hammer-data/Hammer Website/`).
- **Post-call / missed-call transcription and follow-on actions (not live phone answering):** Hammer is **not** an AI that **answers** the dealership's inbound phone line for shoppers — **no live call answering** at any rooftop. Positioning from demo materials: **transcribe** missed calls / voicemail and **take next steps** from that (text-back, CRM, executing on what was promised after a rep-handled conversation where audio was captured). Do not describe Hammer as replacing the store's phone receptionist or picking up rings before staff.
- **Marketplace listings (MarketPoster):** Install the **MarketPoster Chrome extension**, open your **listing site**, select one or multiple vehicles, click **Post** — the tool **fills Marketplace listing fields** with vehicle details so staff are not retyping; messaging in materials emphasizes **time saved** and **leads faster on Facebook** (see ingested video transcript under `raw/hammer-data/` and MarketPoster PDF).
- **Marketplace messaging (Hammer Connect):** Facebook Marketplace thread → routed into Hammer next to SMS/CRM; **first reply** goes out as **text** in the SMS channel (per Hammer Connect PDF / prior wiki summary). **Hammer Connect is included in MarketPoster** at **no additional monthly charge**; **standalone** Connect-only (no MarketPoster) is **$199/month**.

### Facebook AIA — lead path and ops (from AIA Guide)

- **Lead path:** Shopper sees sponsored ad (Feed, Stories, Marketplace, etc.) → lands on **Marketplace listing** for the vehicle → sends a **Facebook message** → **Hammer answers** like any other Facebook message → **lead created in CRM**.
- **Inventory in ads:** Carousel of up to **25 vehicles** from live inventory; system **auto-rotates** if the dealer has more than 25 (dealers cannot hand-pick units per guide).
- **Targeting:** Meta targets in-market vehicle shoppers; dealer can adjust some targeting; default **~50 mile** radius (multiple directional campaigns possible for wider coverage).
- **Costs:** (1) **Hammer fee** — **$299/month** (month-to-month) covers Hammer running the campaigns and responding to every lead; (2) **Facebook ad spend** — **$15/day minimum**, paid separately as ad spend and **not included** in the $299 Hammer fee. The $15/day covers the dealer's **full inventory** regardless of how many vehicles are on the lot — it is not per car. Dealers may increase the daily budget above $15 for more reach; $15/day is the floor.
- **Results:** View in Facebook **Ad Center**; guide cites **≥50% message-volume lift** (sales claim).
- **Limitation:** At time of guide, **cannot distinguish** AIA-sourced messages from other Facebook messages (product may change).

## Positioning vs alternatives

- Differentiator vs generic chatbots: trained on **dealer-specific** inventory, hours, policies; avoids “instant obvious bot” via delays and richer dialogue (per transcripts).
- Historical arc: **Human virtual BDC (~150 people)** scaled first; switched to AI once benchmarks showed AI outperforming humans (podcast / sales story).

## Integrations mentioned

Website / third-party leads (Cars Commerce, Trader, CarGurus, Carpages, TrueCar-style sources, **Carsforsale**, **Carzing**), many CRMs (DealerTrack, Tekion, DealerCenter, CDK, eLeads, VinSolutions, etc.). **Service-drive proactive mining** described as **not** current focus in one transcript (sales-side CRM + inventory); service scheduling links supported when customer asks.

## Metrics cited in sources (treat as sales claims)

| Metric | Context |
|--------|---------|
| ~**80%** engagement | Customer replies back to AI (definition per rep) |
| ~**31%** lift | Converted leads → appointments / credit-app style actions vs pre-Hammer baseline (stated aggregate) |
| **2,500+** dealerships | Marketing one-pager |
| **48%** of leads after hours | Podcast / Hammer narrative |

## Pricing (current retail — US and Canada)

Monthly subscription prices by lot size. No trials offered.

### Hammer Drive (US — USD)

| Inventory | Monthly price |
|-----------|--------------|
| 10–30 cars | $299 |
| 31–60 cars | $399 |
| 61–80 cars | $599 |
| 80+ cars | $999 |

### Hammer Drive (Canada — CAD)

| Inventory | Monthly price (CAD) |
|-----------|---------------------|
| 10–30 cars | $299 CAD |
| 31–60 cars | $399 CAD |
| 61–80 cars | $599 CAD |
| 80+ cars | $1,299 CAD |

### Facebook AIA

Facebook AIA is **month-to-month** with two separate charges:

| Item | Cost | Notes |
|------|------|-------|
| Hammer fee (Facebook AIA) | **$299 / month** | Month-to-month; covers Hammer running the campaigns and responding to every lead |
| Facebook ad spend | **$15 / day minimum** | Paid directly as ad spend; **not included** in the $299 Hammer fee |

**Critical pricing points to always communicate:**

- The **$15/day ad spend is separate from and not included in the $299/month** Hammer fee — it is an additional daily cost.
- The **$15/day covers the dealer's entire inventory** — it is not $15 per vehicle. Whether the dealer has 20 cars or 200 cars on the lot, the minimum ad spend remains **$15/day for all vehicles combined**.
- Dealers **can increase the daily ad spend** above $15 if they want more reach or impressions, but **$15/day is the minimum** required.
- At $15/day the monthly ad spend is roughly **$450/month** (on top of the $299 Hammer fee), making the all-in starting cost approximately **$749/month**.

### MarketPoster (US — USD)

| Seats | Monthly price |
|-------|--------------|
| 1 user | $199 |
| 3 users | $299 |
| 5 users | $599 |
| Additional user | +$50 |

**Hammer Connect included:** **Hammer Connect** (Marketplace conversations routed into Hammer with **first reply via text/SMS**) is **included with MarketPoster at no additional charge** — it is **not** a separate monthly add-on on top of the seat prices above.

**Hammer Connect standalone:** If the dealer wants **only Hammer Connect** and **not** MarketPoster (messaging-only SKU): **$199/month**.

### Craigslist posting (Hammer Drive — usage fee, USD)

Posting inventory to **Craigslist through Hammer** is part of **Hammer Drive**; billing is **per post**, not unlimited free listings.

| Item | Fee |
|------|-----|
| Each Craigslist vehicle post | **$5.99 per post** |

**There are no free Craigslist postings** — every post incurs this fee when the dealer uses the feature.

**Dealer-controlled schedule:** **How often** and **when** inventory posts are **fully dealer-controlled** and **customizable** — examples include posting **daily**, **every other day**, or on lighter cadences/patterns the store prefers (specific days/times, rotation rules, etc.). There is **no** fixed Hammer posting cadence imposed on dealers; Hammer executes **whatever schedule they configure**. Total spend rises with posting volume since **every post is still $5.99**.

**Craigslist lead response:** Hammer **responds to inbound Craigslist leads** using the same AI engagement model as other channels — instant reply, persistent follow-up, and CRM logging all apply.

## Go-live timeline (implementation)

- After onboarding and required integrations are in place, dealers should **expect to go live with Hammer services in under 72 business hours**. Count **business hours** (weekday working time), not raw calendar hours or weekends.

## Commercial notes (time-stamped; may change)

- Example **Canadian group** pricing in transcript: ~**CAD $2,199**/rooftop/month, **~25% group** discount to ~**CAD $1,699** for seven rooftops; **month-to-month**, no long-term contract / no setup fee (per that call).
- **Trial / renewal / cold close** flow (**sales narratives in `raw/hammer-data/`; verify live policy**): rep requests email reply **\"I approve\"**, a **nominal (~$5 verbal)** card charge contemporaneous with **account activation/onboarding**, and positions **free trial countdown** beginning only after integrations with listed lead feeds are complete—not from first outbound email ping. Cancelling verbally tied to alerting **before the final trial day** (rep frames **day 13** as the decision point) **dashboard `Ask support`**, **website help/contact links**, or rep contact details. Details align across **`Hammer_Sales_Renewal_and_Dealer_Trial_Activation.md`** ([file](../raw/hammer-data/Hammer_Sales_Renewal_and_Dealer_Trial_Activation.md)) + newer redacted synopsis **[Hammer_Sales_Pitch_Call_Deal_Closed_Redacted.md](../raw/hammer-data/Hammer_Sales_Pitch_Call_Deal_Closed_Redacted.md)** (**card/EIN/email/phones stripped**).

### Account activation UI (Welcome email flow)

When a new dealer account is created, activation via the **Welcome to Hammer** email follows this **fixed screen order**:

1. **Activate your account** (link from Welcome email)
2. **Create password** — minimum **10 characters** (longer is fine; never say "exactly ten")
3. **Card entry** — the **next screen immediately after password** is where the dealer enters a payment card for **month-to-month billing on file**. The dealer types the card **in the Hammer account UI** (never collected on voice AI or chat).
4. After card is on file, a **live Hammer representative** typically reaches out to walk through account setup (about **5–10 minutes** on that call).

**Billing:** putting a card on file during activation does **not** by itself start monthly service billing; charges align with live-rep onboarding and dealership go-live (see commercial notes below).

### Dashboard narration (trial onboarding transcripts)

Recorded walkthrough snippets (**UI may drift**): onboarding **banner** flagged at top post‑welcome email; **`Agent settings`** controls assistant display name (**default conversational name cited on calls as `Emma`**); **`Questions and answers`** section seeds dealership FAQs with optional crawler backfill within a few days if dealer busy; Hammer operations may **contact marketplaces/third‑party feeds** automatically to finish wiring integrations.

## Related companies / people (from podcast)

- **DealerBids** — separate private-party acquisition platform founded by ex-Hammer leadership (John McIntyre); distinct product from Hammer AI.

## Source of truth in this repo

- Immutable copies: [`raw/hammer-data/`](../raw/hammer-data/)
- Ingest manifest: [source-hammer-data.md](source-hammer-data.md)


## Cross-links

- [overview.md](overview.md) — VibeVoice project map (this entity is external domain knowledge stored alongside the repo wiki).
