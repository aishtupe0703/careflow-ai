
from types import SimpleNamespace

from app.main import app, get_ticket_classifier
from app.services import classification_service as service


def test_ai_classification_saved_to_database(client, monkeypatch):
    # Simulate an OpenAI response.
    def fake_openai(message):
        return SimpleNamespace(
            category="billing",
            priority="high",
            assigned_team="billing",
            requires_human_review=True,
            summary="Patient has a billing question.",
        )

    monkeypatch.setattr(
        service,
        "classify_with_openai",
        fake_openai,
    )

    # Replace the fixture's rule-based classifier override
    # with the real hybrid service, using our fake OpenAI.
    app.dependency_overrides[get_ticket_classifier] = (
        lambda: service.classify_for_ticket
    )

    response = client.post(
        "/tickets",
        json={
            "patient_name": "Demo Patient",
            "message": "There appears to be a charge I do not recognize.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "billing"
    assert data["priority"] == "high"
    assert data["assigned_team"] == "billing"
    assert data["requires_human_review"] is True

    # Verify the classification was saved in PostgreSQL.
    tickets_response = client.get("/tickets")

    assert tickets_response.status_code == 200

    assert any(
        ticket["id"] == data["id"]
        and ticket["category"] == "billing"
        for ticket in tickets_response.json()
    )

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_reject_empty_message(client):
    response = client.post(
        "/tickets",
        json={
            "patient_name": "Demo Patient",
            "message": "",
        },
    )

    assert response.status_code == 422


def test_create_ticket(client):
    response = client.post(
        "/tickets",
        json={
            "patient_name": "Demo Patient",
            "message": "I want to book an appointment",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["category"] == "appointment"
    assert data["priority"] == "normal"
    assert data["assigned_team"] == "reception"
    assert data["status"] == "new"
    assert data["requires_human_review"] is True


def test_ticket_is_saved_in_database(client):
    response = client.post(
        "/tickets",
        json={
            "patient_name": "Demo Patient",
            "message": "I need an invoice",
        },
    )

    assert response.status_code == 201

    ticket_id = response.json()["id"]

    list_response = client.get("/tickets")

    assert list_response.status_code == 200

    tickets = list_response.json()

    assert any(
        ticket["id"] == ticket_id
        for ticket in tickets
    )


def test_emergency_ticket_routing(client):
    response = client.post(
        "/tickets",
        json={
            "patient_name": "Demo Patient",
            "message": "I have severe chest pain",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["category"] == "potential_emergency"
    assert data["priority"] == "critical"
    assert data["requires_human_review"] is True

def test_ticket_count_starts_at_zero(client):
    response = client.get("/tickets")

    assert response.status_code == 200
    assert response.json() == []