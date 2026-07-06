// Prerender the landing page to a committed static HTML snapshot.
//
// Why this exists: the marketing site is a fully client-rendered vanilla-TS SPA,
// so `view-source:` (and non-JS crawlers / compliance reviewers like Textedly)
// only saw an empty "Loading…" shell. This script loads the *built* site in a
// real headless browser, lets it render, and captures the resulting `#app` DOM
// into `prerendered/landing.snapshot.html`. A dependency-free Vite plugin
// (see vite.config.ts) then injects that snapshot into `dist/index.html` on every
// build — so the deployed HTML contains real content with NO browser needed at
// deploy time.
//
// Run it whenever the marketing copy/layout changes:  npm run prerender
//
// Chrome discovery: uses PUPPETEER_EXECUTABLE_PATH if set, otherwise probes the
// usual Windows/macOS/Linux install locations for Chrome or Edge. We use
// puppeteer-core (no bundled Chromium download) so installs stay light and
// deploys never try to fetch a browser.

import { createServer } from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const distDir = path.join(webRoot, "dist");
const outDir = path.join(webRoot, "prerendered");
const outFile = path.join(outDir, "landing.snapshot.html");

// Panel routes are also snapshotted (each opens its nav panel on boot), so
// /faq, /reviews, etc. can ship as real static pages with *visible* content
// for crawlers/AI engines instead of SPA-fallback copies of the homepage.
// Written to prerendered/route-<name>.snapshot.html; the prerender-inject
// plugin (vite.config.ts) turns each into dist/<name>/index.html at build.
const PANEL_ROUTES = ["reviews", "faq", "about", "support", "terms", "privacy"];

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ico": "image/x-icon",
  ".map": "application/json; charset=utf-8",
};

function findChrome() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) return process.env.PUPPETEER_EXECUTABLE_PATH;
  const candidates = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/microsoft-edge",
  ];
  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) return p;
    } catch {
      /* ignore */
    }
  }
  return null;
}

/** Serve the built dist/ statically. /api/* returns 404 fast so the app boots on fallbacks. */
function startStaticServer() {
  const server = createServer((req, res) => {
    const url = (req.url || "/").split("?")[0];
    if (url.startsWith("/api/")) {
      res.writeHead(404).end();
      return;
    }
    let rel = decodeURIComponent(url);
    if (rel === "/" || rel.endsWith("/")) rel += "index.html";
    const filePath = path.join(distDir, path.normalize(rel));
    if (!filePath.startsWith(distDir)) {
      res.writeHead(403).end();
      return;
    }
    fs.readFile(filePath, (err, data) => {
      if (err) {
        // SPA fallback so client routes still resolve to the app.
        fs.readFile(path.join(distDir, "index.html"), (e2, idx) => {
          if (e2) return res.writeHead(404).end();
          res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" }).end(idx);
        });
        return;
      }
      const ext = path.extname(filePath).toLowerCase();
      res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" }).end(data);
    });
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

async function main() {
  if (!fs.existsSync(path.join(distDir, "index.html"))) {
    console.error("[prerender] dist/index.html not found — run `npm run build` first.");
    process.exit(1);
  }

  const chromePath = findChrome();
  if (!chromePath) {
    console.error(
      "[prerender] Could not find Chrome/Edge. Set PUPPETEER_EXECUTABLE_PATH to a Chromium binary and retry.",
    );
    process.exit(1);
  }

  const server = await startStaticServer();
  const { port } = server.address();
  const base = `http://127.0.0.1:${port}/`;
  console.log(`[prerender] serving dist at ${base} (chrome: ${chromePath})`);

  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
  });

  try {
    const page = await browser.newPage();
    // A realistic desktop viewport so responsive CSS picks the full layout.
    await page.setViewport({ width: 1280, height: 900 });

    const banner =
      "<!-- AUTO-GENERATED by scripts/prerender.mjs — do not edit by hand. " +
      "Regenerate with `npm run prerender`. Injected into dist/ at build time. -->\n";
    fs.mkdirSync(outDir, { recursive: true });

    const snapshotRoute = async (route, file, { expectPanel } = {}) => {
      await page.goto(base.replace(/\/$/, "") + route, {
        waitUntil: "networkidle0",
        timeout: 45_000,
      });

      // Wait until the app has actually rendered real content into #app —
      // and, for panel routes, until the panel overlay is actually open.
      await page.waitForFunction(
        (needPanel) => {
          const app = document.querySelector("#app");
          if (!app || !app.querySelector(".app-shell") || app.innerHTML.length < 2000) return false;
          if (needPanel) return !!app.querySelector(".nav-panel-layer.is-open");
          return true;
        },
        { timeout: 30_000 },
        !!expectPanel,
      );

      // Give CSS-driven layout a beat to settle (no timers depended on).
      await new Promise((r) => setTimeout(r, 250));

      let html = await page.$eval("#app", (el) => el.innerHTML);

      // Safety: strip any <script> that may have landed inside #app so the
      // injected static snapshot can never double-execute code.
      html = html.replace(/<script\b[\s\S]*?<\/script>/gi, "");

      if (!html || html.length < 2000) {
        throw new Error(`Rendered #app content too small for ${route} (${html.length} bytes).`);
      }

      fs.writeFileSync(file, banner + html + "\n", "utf8");
      console.log(`[prerender] ${route} -> ${path.relative(webRoot, file)} (${html.length} bytes).`);
    };

    await snapshotRoute("/", outFile);
    for (const name of PANEL_ROUTES) {
      await snapshotRoute(`/${name}`, path.join(outDir, `route-${name}.snapshot.html`), {
        expectPanel: true,
      });
    }
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch((err) => {
  console.error("[prerender] failed:", err);
  process.exit(1);
});
