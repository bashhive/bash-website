"""Validate a HiveSec Sentinel dispatch event and update the public alert feed."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MAX_ALERTS = 20
SAFE_ID = re.compile(r"^[a-zA-Z0-9._-]{1,80}$")
SEVERITIES = {"critical", "warning", "info"}


def clean_text(value: Any, *, maximum: int) -> str:
    if not isinstance(value, str):
        raise ValueError("Alert text fields must be strings")
    cleaned = "".join(char for char in value.strip() if char >= " " or char in "\n\t")
    if not cleaned:
        raise ValueError("Alert text fields cannot be empty")
    return cleaned[:maximum]


def validate_alert(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Unsupported alert payload")
    alert_id = payload.get("id")
    if (
        not isinstance(alert_id, str)
        or not alert_id.startswith("hivesec-")
        or not SAFE_ID.fullmatch(alert_id)
    ):
        raise ValueError("Invalid alert ID")
    severity = payload.get("severity")
    if severity not in SEVERITIES:
        raise ValueError("Invalid alert severity")
    published_at = clean_text(payload.get("published_at"), maximum=40)
    parsed = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Alert timestamp must include a timezone")
    source = clean_text(payload.get("source"), maximum=80)
    if source != "HiveSec Sentinel":
        raise ValueError("Invalid alert source")
    return {
        "id": alert_id,
        "title": clean_text(payload.get("title"), maximum=160),
        "message": clean_text(payload.get("message"), maximum=6000),
        "severity": severity,
        "source": source,
        "published_at": parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat(),
    }


def update_feed(event_path: Path, feed_path: Path) -> None:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    alert = validate_alert(event.get("client_payload"))
    if feed_path.is_file():
        feed = json.loads(feed_path.read_text(encoding="utf-8"))
    else:
        feed = {"schema_version": 1, "alerts": []}
    current = feed.get("alerts") if isinstance(feed, dict) else []
    if not isinstance(current, list):
        current = []
    alerts = [alert, *(item for item in current if item.get("id") != alert["id"])]
    output = {
        "schema_version": 1,
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "alerts": alerts[:MAX_ALERTS],
    }
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = feed_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, feed_path)


if __name__ == "__main__":
    update_feed(Path(os.environ["GITHUB_EVENT_PATH"]), Path("alerts/feed.json"))
