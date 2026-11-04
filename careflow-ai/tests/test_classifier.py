
from app.classifier import classify_ticket


def test_appointment_classification():
    result = classify_ticket(
        "I want to reschedule my appointment"
    )

    assert result["category"] == "appointment"
    assert result["priority"] == "normal"
    assert result["assigned_team"] == "reception"


def test_billing_classification():
    result = classify_ticket(
        "I need a refund for my payment"
    )

    assert result["category"] == "billing"
    assert result["assigned_team"] == "billing"


def test_emergency_classification():
    result = classify_ticket(
        "My father has chest pain and difficulty breathing"
    )

    assert result["category"] == "potential_emergency"
    assert result["priority"] == "critical"
    assert result["requires_human_review"] is True


def test_unknown_message():
    result = classify_ticket(
        "What are your opening hours?"
    )

    assert result["category"] == "general"
    assert result["assigned_team"] == "front_desk"
