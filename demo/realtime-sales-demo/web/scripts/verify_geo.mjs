// Quick local check that GEO assets made it into dist/ and the JSON-LD parses.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dist = path.join(webRoot, "dist");

for (const f of ["robots.txt", "sitemap.xml", "llms.txt", "index.html"]) {
  const p = path.join(dist, f);
  const ok = fs.existsSync(p);
  console.log(`${ok ? "OK " : "MISSING"} dist/${f}${ok ? ` (${fs.statSync(p).size} bytes)` : ""}`);
}

const html = fs.readFileSync(path.join(dist, "index.html"), "utf8");
const blocks = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
console.log(`JSON-LD blocks: ${blocks.length}`);
for (const b of blocks) {
  const o = JSON.parse(b[1]);
  const label = o["@type"] || o["@graph"].map((g) => `${g["@type"]}:${g.name}`).join(", ");
  console.log(`  - ${label} (valid JSON)`);
}

const desc = html.match(/name="description" content="([^"]*)"/);
console.log(`meta description length: ${desc ? desc[1].length : "n/a"}`);
const title = html.match(/<title>(.*?)<\/title>/);
console.log(`title length: ${title ? title[1].length : "n/a"} ("${title?.[1]}")`);
