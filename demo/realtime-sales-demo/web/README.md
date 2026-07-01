# web/ — public website (browser)

What customers see: landing page, **Start call**, voice UI.

**Vercel builds this folder** (`npm run build` → `dist/`).  
**Local:** run `..\2-START-LOCAL-WEB.ps1` after the API is up.

## Main source files

| File | What it does |
|------|----------------|
| **`src/main.ts`** | Voice agent, tools, signup flow (PHASE A/B/C) |
| **`src/pen-challenge-close.ts`** | Closing / signup prompts |
| **`src/pen-challenge-instructions.ts`** | Sales instructions |
| **`src/landing-hero.css`** | Landing page layout and styling |
| **`src/style.css`** | Shared UI styles |

## Safe env vars (optional, public in build)

Only use **`VITE_*`** for non-secret UI settings (voice name, sign-in URL).  
**Never** put `OPENAI_API_KEY` or Hammer passwords in `VITE_*`.

## API calls

The browser talks to **`/api/*`** on the same host (Vercel) or via Vite proxy to port **8780** locally.

## Prerendered content — `view-source:` must show real HTML

The site is a client-rendered SPA, so the raw HTML used to be an empty `Loading…`
shell. Crawlers, link unfurlers, and SMS/compliance reviewers (e.g. **Textedly**)
that don't run JS saw nothing — which blocked approvals. To fix it we bake a static
snapshot of the landing page into the deployed HTML:

- **`scripts/prerender.mjs`** loads the *built* site in headless Chrome (via
  `puppeteer-core` + your local Chrome/Edge — no bundled download) and writes the
  rendered `#app` DOM to **`prerendered/landing.snapshot.html`** (committed).
- A `closeBundle` plugin in **`vite.config.ts`** injects that snapshot into
  `dist/index.html` on every `npm run build`. It only reads a file — **the Vercel
  build needs no browser** and can't fail on a missing Chromium.
- On boot, `main.ts`'s `render()` replaces `#app`, so the snapshot is a pure
  pre-hydration view (it also speeds up first paint).

**Regenerate the snapshot whenever the landing copy/layout changes:**

```powershell
cd demo/realtime-sales-demo/web
npm run prerender   # vite build + headless snapshot → prerendered/landing.snapshot.html
git add prerendered/landing.snapshot.html
```

Point at a specific browser with `PUPPETEER_EXECUTABLE_PATH` if auto-detection
fails. If the snapshot is ever missing, the build still succeeds (it logs a warning
and ships the empty shell) — so a stale/missing snapshot never breaks a deploy, but
it does mean `view-source:` reverts to a shell until you re-run `npm run prerender`.

## Performance — keep first load fast

The landing page must paint without waiting on voice-only code. Rules that keep it that way:

- **Never statically `import` `@elevenlabs/client` (or other voice-only/heavy deps) at the top of `main.ts`.** The SDK (~490 kB) is loaded on demand via `loadElevenLabsClient()` (a cached dynamic `import()`), warmed on first user intent. A static import drags it back onto the first-paint path. Use `import type { … }` for type-only needs.
- **Watch the build output.** The critical entry chunk should stay ~130 kB. `vite.config.ts` sets `chunkSizeWarningLimit: 550` so a regression that re-merges the SDK into the entry (~620 kB) prints a warning.
- **Hashed assets are cached forever.** `vercel.json` sets `Cache-Control: public, max-age=31536000, immutable` on `/assets/*`. Without it Vercel defaults to `max-age=0, must-revalidate`, adding a revalidation round-trip to **every** visit. Don't remove that headers block.
- **Don't make `<head>` resources render-blocking.** Google Fonts load via `rel="preload"` + `onload` swap in `index.html`; keep new third-party CSS non-blocking.
