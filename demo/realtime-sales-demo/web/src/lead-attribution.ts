/** Persist Google click IDs and UTMs across the SPA so /get-started still has them. */

const STORAGE_KEY = "hammer.leadAttribution";

const ATTR_KEYS = [
  "gclid",
  "gbraid",
  "wbraid",
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_term",
  "utm_content",
] as const;

export type LeadAttribution = {
  gclid: string;
  gbraid: string;
  wbraid: string;
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  utm_term: string;
  utm_content: string;
};

function emptyAttribution(): LeadAttribution {
  return {
    gclid: "",
    gbraid: "",
    wbraid: "",
    utm_source: "",
    utm_medium: "",
    utm_campaign: "",
    utm_term: "",
    utm_content: "",
  };
}

function sanitize(value: string): string {
  return value.trim().slice(0, 200);
}

function readStored(): LeadAttribution {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyAttribution();
    const parsed = JSON.parse(raw) as Partial<LeadAttribution>;
    const next = emptyAttribution();
    for (const key of ATTR_KEYS) {
      const value = parsed[key];
      if (typeof value === "string" && value) next[key] = sanitize(value);
    }
    return next;
  } catch {
    return emptyAttribution();
  }
}

function writeStored(value: LeadAttribution): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  } catch {
    /* private mode / quota */
  }
}

/** Capture query params on first load. Later /get-started navigations keep the first click. */
export function captureLeadAttribution(search: string = window.location.search): LeadAttribution {
  const params = new URLSearchParams(search);
  const stored = readStored();
  let changed = false;
  for (const key of ATTR_KEYS) {
    const incoming = sanitize(params.get(key) ?? "");
    if (incoming && incoming !== stored[key]) {
      stored[key] = incoming;
      changed = true;
    }
  }
  if (changed) writeStored(stored);
  return stored;
}

export function getLeadAttribution(): LeadAttribution {
  return readStored();
}

export function leadAttributionFields(attr: LeadAttribution = getLeadAttribution()): Record<string, string> {
  const out: Record<string, string> = {};
  for (const key of ATTR_KEYS) {
    if (attr[key]) out[key] = attr[key];
  }
  return out;
}
