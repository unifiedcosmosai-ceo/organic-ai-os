"""
LAYER 12/13 OPS: WEBHOOK-OUT (v6)
Push-Benachrichtigungen bei Organismus-Events (fitness_drop, new_champion,
alarm, validation_failure, coevolution, test) via HTTP POST.
Nur stdlib (urllib) - keine Abhaengigkeiten.

Konfiguration: memory/webhooks.json
    [{"url": "https://example.com/hook", "events": ["alarm", "fitness_drop"], "enabled": true}]
"""

import json
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import List

DEFAULT_CONFIG = Path("memory") / "webhooks.json"


def load_config(path: Path = DEFAULT_CONFIG) -> list:
    """Liest die Webhook-Liste; fehlende/kaputte Datei -> leere Liste."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else [data]
    except Exception:
        return []


def save_config(hooks: list, path: Path = DEFAULT_CONFIG):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(hooks, indent=2, ensure_ascii=False))


class WebhookDispatcher:
    """Feuert Events an passende Hooks und loggt jede Zustellung."""

    def __init__(self, hooks: list = None, timeout: float = 5.0):
        self.hooks = hooks if hooks is not None else load_config()
        self.timeout = timeout
        self.sent: List[dict] = []

    def _matching(self, event: str) -> list:
        return [h for h in self.hooks
                if h.get("enabled", True) and event in h.get("events", [])]

    def fire(self, event: str, payload: dict) -> dict:
        """Versendet einen Event an alle passenden Hooks, protokolliert Entry."""
        results = []
        for hook in self._matching(event):
            ok, status = self._post(hook, event, payload)
            results.append({"url": hook.get("url"), "ok": ok, "status": status})
        entry = {"event": event, "time": datetime.now().isoformat(),
                 "targets": len(results), "results": results}
        self.sent.append(entry)
        return entry

    def _post(self, hook: dict, event: str, payload: dict):
        body = json.dumps({"event": event, "payload": payload,
                           "ts": datetime.now().isoformat()}).encode()
        req = urllib.request.Request(
            hook["url"], data=body, method="POST",
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return True, resp.status
        except Exception:
            return False, None

    def summary(self) -> dict:
        ok = sum(1 for e in self.sent for r in e["results"] if r["ok"])
        return {"hooks": len(self.hooks), "sent": len(self.sent),
                "delivered_ok": ok, "last": self.sent[-1] if self.sent else None}