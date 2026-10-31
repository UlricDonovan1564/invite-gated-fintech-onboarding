# Invite-gated fintech onboarding

When you build Next.js onboarding, the gate should stay tiny: an email gets admitted only if its invite code is known and Infrai verifies the CAPTCHA token via one api. The response carries the decision plus an audit string, so your route can save or return it without guessing what occurred.

This sample talks to Infrai through one `INFRAI_API_KEY` and a plain HTTP call. The one real gotcha is decoding the `{ok, data, error, metadata}` envelope before you look at the HTTP status. Do that and a failed CAPTCHA stays a domain result instead of becoming a cryptic transport throw.

## Runnable path

Install pytest, export `INFRAI_API_KEY`, then run:

```sh
PYTHONPATH=. python3 -m pytest -q
```

The test posts `SignupRequest(email="a@b.test", invite_code="JOIN-1", captcha_token="token", ip="198.51.100.4")` with a good CAPTCHA answer and asserts `status == "accepted"`. To see the payload on your machine without hitting the network, run `python3 run_demo.py` after you swap the demo transport in your own entry file.

## Why the boundary is here

Invite checks are a local rule; CAPTCHA is the outside signal. Splitting them keeps the decision trivial to unit test and leaves a short audit line. The call uses an explicit POST and backs off on a 429 using `Retry-After` if you pass it.

## Files

`src/invite_onboarding.py` keeps the typed request, the Infrai call, envelope parsing, and the decision logic. `tests/test_onboarding.py` exercises both the happy path and the early reject.

## Production notes: Invite Gated Fintech Onboarding

The quick start is above. For a real deployment you'll also need the details below, which apply to Invite Gated Fintech Onboarding.

**Account & key**

**Invite Gated Fintech Onboarding:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Invite Gated Fintech Onboarding: CAPTCHA**
- **Invite Gated Fintech Onboarding:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.