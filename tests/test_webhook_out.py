"""Tests fuer den Webhook-Out Dispatcher (v6, Layer 12/13 ops)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from webhook_out import WebhookDispatcher, load_config, save_config


class FakeResponse:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _fake_ok(request, timeout=None):
    capt["last_request"] = request
    return FakeResponse(200)


capt = {}


def test_load_config_missing_returns_empty(tmp_path):
    assert load_config(tmp_path / "nope.json") == []


def test_save_and_load_roundtrip(tmp_path):
    p = tmp_path / "webhooks.json"
    hooks = [{"url": "http://x", "events": ["alarm"], "enabled": True}]
    save_config(hooks, p)
    assert load_config(p) == hooks


def test_load_config_broken_returns_empty(tmp_path):
    p = tmp_path / "webhooks.json"
    p.write_text("{kaputt")
    assert load_config(p) == []


def test_fire_filters_nonmatching_events(monkeypatch):
    monkeypatch.setattr("webhook_out.urllib.request.urlopen", _fake_ok)
    d = WebhookDispatcher([{"url": "http://x", "events": ["alarm"]}])
    entry = d.fire("evolution", {"a": 1})
    assert entry["event"] == "evolution"
    assert entry["targets"] == 0
    assert entry["results"] == []
    assert d.summary()["sent"] == 1


def test_fire_posts_matching_hook(monkeypatch):
    monkeypatch.setattr("webhook_out.urllib.request.urlopen", _fake_ok)
    d = WebhookDispatcher([{"url": "http://x", "events": ["alarm"]}])
    entry = d.fire("alarm", {"fitness": 0.2})
    assert entry["targets"] == 1
    assert entry["results"][0]["ok"] is True
    assert entry["results"][0]["status"] == 200
    assert capt["last_request"].method == "POST"


def test_fire_posts_json_content_type(monkeypatch):
    monkeypatch.setattr("webhook_out.urllib.request.urlopen", _fake_ok)
    d = WebhookDispatcher([{"url": "http://x", "events": ["e"]}])
    d.fire("e", {"k": 1})
    req = capt["last_request"]
    assert req.headers.get("Content-type") == "application/json"
    body = json.loads(req.data.decode())
    assert body["event"] == "e"
    assert body["payload"] == {"k": 1}


def test_fire_failure_reported_ok_false(monkeypatch):
    def _boom(request, timeout=None):
        raise ConnectionError("netz weg")

    monkeypatch.setattr("webhook_out.urllib.request.urlopen", _boom)
    d = WebhookDispatcher([{"url": "http://x", "events": ["alarm"]}])
    entry = d.fire("alarm", {})
    assert entry["results"][0]["ok"] is False
    assert entry["results"][0]["status"] is None


def test_disabled_hook_skipped(monkeypatch):
    monkeypatch.setattr("webhook_out.urllib.request.urlopen", _fake_ok)
    hooks = [
        {"url": "http://a", "events": ["e"], "enabled": False},
        {"url": "http://b", "events": ["e"], "enabled": True},
    ]
    d = WebhookDispatcher(hooks)
    d.fire("e", {})
    assert d.sent[-1]["targets"] == 1


def test_summary_counts_and_last():
    d = WebhookDispatcher([{"url": "http://x", "events": ["e"]}])
    d.fire("e", {"i": 1})
    d.fire("e", {"i": 2})
    s = d.summary()
    assert s["hooks"] == 1
    assert s["sent"] == 2
    assert s["last"]["event"] == "e"