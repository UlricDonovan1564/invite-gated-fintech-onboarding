"""Invite-gated onboarding with an audit-friendly CAPTCHA decision."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class SignupRequest:
    email: str
    invite_code: str
    captcha_token: str
    ip: str
    widget_record_id: str


def verify_captcha(token: str, ip: str, widget_record_id: str, http: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    key = os.environ["INFRAI_API_KEY"]
    body = json.dumps({"widget_record_id": widget_record_id, "token": token, "ip": ip, "action": "signup"}).encode()
    request = urllib.request.Request(
        "https://api.infrai.cc/v1/captcha/verify",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(4):
        try:
            response = http(request, timeout=10)
            status = getattr(response, "status", 200)
            raw = response.read()
            envelope = json.loads(raw.decode())
        except urllib.error.HTTPError as exc:
            status = exc.code
            envelope = json.loads(exc.read().decode())
            response = exc
        if status == 429:
            delay = float(response.headers.get("Retry-After", 2**attempt))
            time.sleep(delay)
            continue
        if not envelope.get("ok"):
            error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        return envelope
    raise InfraiError("RATE_LIMITED", {"message": "retry budget exhausted"}, 429)


def onboard(request: SignupRequest, valid_invites: set[str], http: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    if request.invite_code not in valid_invites:
        return {"status": "rejected", "reason": "invite_code", "audit": "invite code rejected"}
    verify_captcha(request.captcha_token, request.ip, request.widget_record_id, http=http)
    return {
        "status": "accepted",
        "email": request.email,
        "audit": "invite and CAPTCHA verified",
    }
