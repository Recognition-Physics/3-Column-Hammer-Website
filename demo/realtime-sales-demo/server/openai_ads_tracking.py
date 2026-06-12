"""OpenAI Ads Conversions API client - sends page view / form conversion events.

Events are received from the browser tracker (web/public/openai-tracker.js)
via POST /api/track in app.py and forwarded server-side to OpenAI, so the
Conversions API key never reaches the browser.

Env vars (Vercel project settings in production, server/.env locally):
  OPENAI_ADS_PIXEL_ID              - from Ads Manager -> Conversions tab
  OPENAI_ADS_CONVERSIONS_API_KEY   - sk-svcacct-... key from the same tab
  OPENAI_ADS_VALIDATE_ONLY         - "true" = OpenAI checks events but does
                                     not count them as real conversions
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
import uuid

import httpx

logger = logging.getLogger("openai_ads_tracking")

_DEFAULT_EVENTS_URL = "https://bzr.openai.com/v1/events"

# Browser event name -> (OpenAI standard event type, data.type)
EVENT_TYPES = {
    "page_view": ("page_viewed", "contents"),
    "form_submission": ("lead_created", "customer_action"),
}


def _pixel_id() -> str:
    return os.environ.get("OPENAI_ADS_PIXEL_ID", "").strip()


def _api_key() -> str:
    return os.environ.get("OPENAI_ADS_CONVERSIONS_API_KEY", "").strip()


def _events_url() -> str:
    return os.environ.get("OPENAI_ADS_EVENTS_URL", "").strip() or _DEFAULT_EVENTS_URL


def validate_only() -> bool:
    return os.environ.get("OPENAI_ADS_VALIDATE_ONLY", "").strip().lower() in ("1", "true", "yes")


def tracking_configured() -> bool:
    return bool(_pixel_id() and _api_key())


def sha256_normalized(value: str) -> str:
    """Hash a value the way OpenAI requires: trimmed, lowercased, hex digest."""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()


def build_event(
    event_name: str,
    source_url: str,
    ip_address: str = "",
    user_agent: str = "",
    email: str = "",
) -> dict | None:
    """Build a Conversions API event dict, or None for unknown event names."""
    mapped = EVENT_TYPES.get(event_name)
    if not mapped or not source_url:
        return None
    event_type, data_type = mapped

    user: dict = {}
    if ip_address:
        user["ip_address"] = ip_address
    if user_agent:
        user["user_agent"] = user_agent
    if email and "@" in email:
        user["email_sha256"] = sha256_normalized(email)

    prefix = "pv" if event_name == "page_view" else "form"
    event: dict = {
        "id": f"{prefix}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
        "type": event_type,
        "timestamp_ms": int(time.time() * 1000),
        "source_url": source_url,
        "action_source": "web",
        "data": {"type": data_type},
    }
    if user:
        event["user"] = user
    return event


async def send_conversion_event(
    event_name: str,
    source_url: str,
    ip_address: str = "",
    user_agent: str = "",
    email: str = "",
) -> bool:
    """Send one event to the OpenAI Conversions API. Never raises."""
    if not tracking_configured():
        return False
    event = build_event(event_name, source_url, ip_address, user_agent, email)
    if event is None:
        return False
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{_events_url()}?pid={_pixel_id()}",
                headers={
                    "Authorization": f"Bearer {_api_key()}",
                    "Content-Type": "application/json",
                },
                json={"validate_only": validate_only(), "events": [event]},
            )
        if resp.status_code >= 400:
            logger.warning(
                "openai_ads event rejected (%s): %s", resp.status_code, resp.text[:500]
            )
            return False
        logger.info(
            "openai_ads %s sent%s", event["type"], " [validate-only]" if validate_only() else ""
        )
        return True
    except httpx.HTTPError as exc:
        logger.warning("openai_ads event failed to send: %s", exc)
        return False
