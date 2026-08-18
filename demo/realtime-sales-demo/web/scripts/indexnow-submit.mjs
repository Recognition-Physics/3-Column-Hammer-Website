#!/usr/bin/env node
// Submit URLs to IndexNow (Bing + partners). Run after every deploy that
// changes indexable content:
//   node scripts/indexnow-submit.mjs                 -> submits every sitemap URL
//   node scripts/indexnow-submit.mjs /guides/foo ... -> submits specific paths
// The key file public/<KEY>.txt must stay deployed at the site root.

const HOST = "www.hammertime.com";
const KEY = "0226dbbd87104da38748bec21f465e31";

async function sitemapUrls() {
  const res = await fetch(`https://${HOST}/sitemap.xml`);
  const xml = await res.text();
  return [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
}

const args = process.argv.slice(2);
const urlList = args.length
  ? args.map((p) => (p.startsWith("http") ? p : `https://${HOST}${p}`))
  : await sitemapUrls();

const res = await fetch("https://api.indexnow.org/indexnow", {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=utf-8" },
  body: JSON.stringify({
    host: HOST,
    key: KEY,
    keyLocation: `https://${HOST}/${KEY}.txt`,
    urlList,
  }),
});

console.log(`IndexNow: HTTP ${res.status} for ${urlList.length} URLs`);
urlList.forEach((u) => console.log(`  ${u}`));
if (!res.ok) {
  console.error(await res.text());
  process.exit(1);
}
