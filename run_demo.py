from src.invite_onboarding import SignupRequest, onboard


if __name__ == "__main__":
    print(onboard(SignupRequest("member@example.com", "FINTECH-2026", "demo-token", "203.0.113.9", "demo-widget-record-id"), {"FINTECH-2026"}))
