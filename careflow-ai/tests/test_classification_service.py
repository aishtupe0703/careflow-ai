
from types import SimpleNamespace

from app.services import classification_service as service


def test_ai_appointment_classification(monkeypatch):
    def fake_openai(message):
        return SimpleNamespace(
            category="appointment",
            priority="normal",
            assigned_team="reception",
            requires_human_review=True,
            summary="Patient wants to reschedule.",
        )

    monkeypatch.setattr(
        service, "classify_with_openai", fake_openai
    )

    result = service.classify_for_ticket(
        "Could I move my consultation to Friday?"
    )

    assert result["category"] == "appointment"
    assert result["assigned_team"] == "reception"
    assert result["requires_human_review"] is True


def test_ai_failure_uses_fallback(monkeypatch):
    def failing_openai(message):
        raise RuntimeError("Simulated API failure")

    monkeypatch.setattr(
        service, "classify_with_openai", failing_openai
    )

    result = service.classify_for_ticket(
        "I need a payment receipt"
    )

    assert result["category"] == "billing"
    assert result["assigned_team"] == "billing"


def test_emergency_bypasses_openai(monkeypatch):
    def should_not_be_called(message):
        raise AssertionError("OpenAI should not be called")

    monkeypatch.setattr(
        service, "classify_with_openai", should_not_be_called
    )

    result = service.classify_for_ticket(
        "My father has chest pain"
    )

    assert result["category"] == "potential_emergency"
    assert result["priority"] == "critical"
    assert result["requires_human_review"] is True
