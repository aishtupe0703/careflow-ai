
from types import SimpleNamespace

from app.services import classification_service as service



def test_classification_records_latency(monkeypatch):
    def fake_openai(message):
        classification = SimpleNamespace(
            category="appointment",
            priority="normal",
            assigned_team="reception",
            requires_human_review=True,
            summary="Appointment request",
        )

        return SimpleNamespace(
            classification=classification,
            model="test-model",
            input_tokens=100,
            output_tokens=30,
            total_tokens=130,
        )

    monkeypatch.setattr(
        service,
        "classify_with_openai",
        fake_openai,
    )

    result = service.classify_for_ticket(
        "Can I visit the clinic on Friday?"
    )

    assert result["classification_source"] == "openai"
    assert "latency_ms" in result
    assert isinstance(result["latency_ms"], float)
    assert result["latency_ms"] >= 0
    assert result["model"] == "test-model"
    assert result["input_tokens"] == 100
    assert result["output_tokens"] == 30
    assert result["total_tokens"] == 130

def test_fallback_records_completion_log(monkeypatch, caplog):
    def failing_openai(message):
        raise RuntimeError("Simulated API failure")

    monkeypatch.setattr(
        service,
        "classify_with_openai",
        failing_openai,
    )

    with caplog.at_level("INFO", logger="uvicorn.error"):
        result = service.classify_for_ticket(
            "An unfamiliar administrative request"
        )

    assert result["classification_source"] == "fallback"
    assert "latency_ms" in result
    assert "classification_completed" in caplog.text


def test_ai_appointment_classification(monkeypatch):
    def fake_openai(message):
        classification = SimpleNamespace(
            category="appointment",
            priority="normal",
            assigned_team="reception",
            requires_human_review=True,
            summary="Patient wants to reschedule.",
        )

        return SimpleNamespace(
            classification=classification,
            model="test-model",
            input_tokens=100,
            output_tokens=30,
            total_tokens=130,
        )

    monkeypatch.setattr(
        service,
        "classify_with_openai",
        fake_openai,
    )

    result = service.classify_for_ticket(
        "Could I move my consultation to Friday?"
    )

    assert result["category"] == "appointment"
    assert result["assigned_team"] == "reception"
    assert result["requires_human_review"] is True
    assert result["classification_source"] == "openai"
    assert result["model"] == "test-model"


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
    assert result["classification_source"] == "fallback"


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

def test_emergency_classification_source(monkeypatch):
    def unexpected_openai(message):
        raise AssertionError("OpenAI should not be called")

    monkeypatch.setattr(
        service,
        "classify_with_openai",
        unexpected_openai,
    )

    result = service.classify_for_ticket(
        "My father has severe chest pain"
    )

    assert result["category"] == "potential_emergency"
    assert result["classification_source"] == "safety_rule"

def test_unknown_message_fallback_is_high_priority(monkeypatch):
    def failing_openai(message):
        raise RuntimeError("Simulated OpenAI outage")

    monkeypatch.setattr(
        service,
        "classify_with_openai",
        failing_openai,
    )

    result = service.classify_for_ticket(
        "My mother suddenly became confused and weak."
    )

    assert result["classification_source"] == "fallback"
    assert result["category"] == "general"
    assert result["priority"] == "high"
    assert result["requires_human_review"] is True