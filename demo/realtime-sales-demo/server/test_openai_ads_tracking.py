"""OpenAI Ads conversion tracking - event building + config checks."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from openai_ads_tracking import (
    build_event,
    sha256_normalized,
    tracking_configured,
    validate_only,
)


class OpenAIAdsTrackingTests(unittest.TestCase):
    def test_sha256_normalizes_case_and_whitespace(self) -> None:
        expected = sha256_normalized("john@example.com")
        self.assertEqual(sha256_normalized("  John@Example.COM  "), expected)
        self.assertEqual(len(expected), 64)

    def test_page_view_event_shape(self) -> None:
        event = build_event(
            "page_view",
            "https://hammer-finalsite.vercel.app/",
            ip_address="203.0.113.1",
            user_agent="Mozilla/5.0",
        )
        assert event is not None
        self.assertEqual(event["type"], "page_viewed")
        self.assertEqual(event["data"], {"type": "contents"})
        self.assertEqual(event["action_source"], "web")
        self.assertEqual(event["source_url"], "https://hammer-finalsite.vercel.app/")
        self.assertEqual(event["user"]["ip_address"], "203.0.113.1")
        self.assertTrue(event["id"].startswith("pv_"))

    def test_form_submission_hashes_email(self) -> None:
        event = build_event(
            "form_submission",
            "https://hammer-finalsite.vercel.app/",
            email="Lead@Dealer.com",
        )
        assert event is not None
        self.assertEqual(event["type"], "lead_created")
        self.assertEqual(event["data"], {"type": "customer_action"})
        self.assertEqual(
            event["user"]["email_sha256"], sha256_normalized("lead@dealer.com")
        )
        self.assertNotIn("ip_address", event["user"])

    def test_unknown_event_or_missing_url_returns_none(self) -> None:
        self.assertIsNone(build_event("clicked_logo", "https://example.com/"))
        self.assertIsNone(build_event("page_view", ""))

    def test_event_ids_are_unique(self) -> None:
        ids = {
            build_event("page_view", "https://example.com/")["id"]  # type: ignore[index]
            for _ in range(50)
        }
        self.assertEqual(len(ids), 50)

    @patch.dict(os.environ, {"OPENAI_ADS_PIXEL_ID": "", "OPENAI_ADS_CONVERSIONS_API_KEY": ""})
    def test_not_configured_without_keys(self) -> None:
        self.assertFalse(tracking_configured())

    @patch.dict(
        os.environ,
        {"OPENAI_ADS_PIXEL_ID": "px_test", "OPENAI_ADS_CONVERSIONS_API_KEY": "sk-test"},
    )
    def test_configured_with_keys(self) -> None:
        self.assertTrue(tracking_configured())

    @patch.dict(os.environ, {"OPENAI_ADS_VALIDATE_ONLY": "true"})
    def test_validate_only_flag(self) -> None:
        self.assertTrue(validate_only())

    @patch.dict(os.environ, {"OPENAI_ADS_VALIDATE_ONLY": ""})
    def test_validate_only_defaults_off(self) -> None:
        self.assertFalse(validate_only())


if __name__ == "__main__":
    unittest.main()
