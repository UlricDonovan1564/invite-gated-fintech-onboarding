import json
import io
import urllib.error

from src.invite_onboarding import SignupRequest, onboard


class FakeResponse:
    status = 200

    def read(self):
        return json.dumps({"ok": True, "data": {"verified": True}, "error": None, "metadata": {}}).encode()


def test_valid_invite_and_captcha_are_accepted(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    def http(request, **kwargs):
        assert json.loads(request.data) == {"widget_record_id": "widget-1", "token": "token", "ip": "198.51.100.4", "action": "signup"}
        return FakeResponse()

    result = onboard(SignupRequest("a@b.test", "JOIN-1", "token", "198.51.100.4", "widget-1"), {"JOIN-1"}, http=http)
    assert result["status"] == "accepted"


def test_unknown_invite_is_rejected_before_remote_call(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    result = onboard(SignupRequest("a@b.test", "NOPE", "token", "198.51.100.4", "widget-1"), {"JOIN-1"}, http=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError()))
    assert result == {"status": "rejected", "reason": "invite_code", "audit": "invite code rejected"}


def test_rate_limit_error_envelope_is_retried(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    monkeypatch.setattr("src.invite_onboarding.time.sleep", lambda seconds: None)
    calls = []

    def http(request, **kwargs):
        calls.append(request)
        if len(calls) == 1:
            raise urllib.error.HTTPError(request.full_url, 429, "rate limited", {"Retry-After": "0"}, io.BytesIO(b'{"ok":false,"error":{"code":"RATE_LIMITED"}}'))
        return FakeResponse()

    result = onboard(SignupRequest("a@b.test", "JOIN-1", "token", "198.51.100.4", "widget-1"), {"JOIN-1"}, http=http)
    assert result["status"] == "accepted"
    assert len(calls) == 2
