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

## Performance — keep first load fast

The landing page must paint without waiting on voice-only code. Rules that keep it that way:

- **Never statically `import` `@elevenlabs/client` (or other voice-only/heavy deps) at the top of `main.ts`.** The SDK (~490 kB) is loaded on demand via `loadElevenLabsClient()` (a cached dynamic `import()`), warmed on first user intent. A static import drags it back onto the first-paint path. Use `import type { … }` for type-only needs.
- **Watch the build output.** The critical entry chunk should stay ~130 kB. `vite.config.ts` sets `chunkSizeWarningLimit: 550` so a regression that re-merges the SDK into the entry (~620 kB) prints a warning.
- **Hashed assets are cached forever.** `vercel.json` sets `Cache-Control: public, max-age=31536000, immutable` on `/assets/*`. Without it Vercel defaults to `max-age=0, must-revalidate`, adding a revalidation round-trip to **every** visit. Don't remove that headers block.
- **Don't make `<head>` resources render-blocking.** Google Fonts load via `rel="preload"` + `onload` swap in `index.html`; keep new third-party CSS non-blocking.
