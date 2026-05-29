# wiki/ — website copy + AI knowledge

Markdown pages the voice agent and website use for answers and UI text.

## Most important file for the public site

- **`demo-public-site-copy.md`** — Headlines, CTAs, and labels shown on the landing page (served via `/api/site_copy`).

Edit this file to change customer-facing wording, then redeploy (or restart local API).

## Other pages

Supporting knowledge for `search_wiki` (product facts, positioning, etc.). Bundled on Vercel deploy via `vercel.json` → `includeFiles`.

Do not put API keys or passwords in this folder — it is public content.
