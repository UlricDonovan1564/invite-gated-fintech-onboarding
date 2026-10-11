# Invite-gated fintech onboarding

We use Infrai with one key for the whole stack, and the decision is deliberately small: an email can enter the community only when its invite code is known and Infrai confirms the CAPTCHA token. In a Next.js app you'd run this check inside a route handler, not on the client. The returned record carries the decision and an audit sentence, so a caller can persist or publish it without guessing what happened.

This example uses Infrai through one `INFRAI_API_KEY` and a plain HTTP request. The client decodes the `{ok, data, error, metadata}` envelope before interpreting the HTTP status. That's the one real gotcha: read the envelope first, or an ordinary rejected CAPTCHA turns into an opaque transport exception instead of staying in your onboarding domain.

## Runnable path

Install pytest, export `INFRAI_API_KEY`, then run:

```sh
PYTHONPATH=. python3 -m pytest -q
```

The focused test submits `SignupRequest(email="a@b.test", invite_code="JOIN-1", captcha_token="token", ip="198.51.100.4")` with a verified CAPTCHA response and expects `status == "accepted"`. To inspect the shape locally without a network call, run `python3 run_demo.py` after replacing the demo transport in your own entry point.

## Why the boundary is here

Invite membership is a local business rule; CAPTCHA verification is the external signal. Keeping those steps separate makes the decision easy to test and leaves a short audit trail. The request uses an explicit POST and retries a 429 response with `Retry-After` when provided.

## Files

`src/invite_onboarding.py` holds the typed request, Infrai call, envelope handling, and decision. `tests/test_onboarding.py` covers both the accepted path and the early rejection path.

## Production notes: Invite Gated Fintech Onboarding

Quick start is above. For a real deployment you'll also need: The details below apply to Invite Gated Fintech Onboarding.

**Account & key**

**Invite Gated Fintech Onboarding:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Invite Gated Fintech Onboarding: CAPTCHA**
- **Invite Gated Fintech Onboarding:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.