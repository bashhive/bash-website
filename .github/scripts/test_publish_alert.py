import json
import tempfile
import unittest
from pathlib import Path

from publish_alert import update_feed


class PublishAlertTests(unittest.TestCase):
    def test_updates_and_deduplicates_bounded_feed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event = root / "event.json"
            feed = root / "feed.json"
            payload = {
                "client_payload": {
                    "schema_version": 1,
                    "id": "hivesec-123",
                    "title": "Security alert",
                    "message": "Patch the affected service.",
                    "severity": "critical",
                    "source": "HiveSec Sentinel",
                    "published_at": "2026-06-29T10:00:00+00:00",
                }
            }
            event.write_text(json.dumps(payload), encoding="utf-8")

            update_feed(event, feed)
            update_feed(event, feed)

            result = json.loads(feed.read_text(encoding="utf-8"))
            self.assertEqual(result["schema_version"], 1)
            self.assertEqual(len(result["alerts"]), 1)
            self.assertEqual(result["alerts"][0]["id"], "hivesec-123")

    def test_rejects_html_control_data_and_invalid_severity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event = root / "event.json"
            payload = {
                "client_payload": {
                    "schema_version": 1,
                    "id": "bad id",
                    "title": "Alert",
                    "message": "Message",
                    "severity": "unknown",
                    "source": "HiveSec Sentinel",
                    "published_at": "2026-06-29T10:00:00+00:00",
                }
            }
            event.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                update_feed(event, root / "feed.json")

    def test_rejects_non_hivesec_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event = root / "event.json"
            event.write_text(
                json.dumps(
                    {
                        "client_payload": {
                            "schema_version": 1,
                            "id": "hivesec-valid",
                            "title": "Alert",
                            "message": "Message",
                            "severity": "info",
                            "source": "Other publisher",
                            "published_at": "2026-06-29T10:00:00+00:00",
                        }
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                update_feed(event, root / "feed.json")


if __name__ == "__main__":
    unittest.main()
