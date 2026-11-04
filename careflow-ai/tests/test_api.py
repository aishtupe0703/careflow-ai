
from fastapi.testclient import TestClient
from app.main import app, tickets
from app.classifier import classify_ticket

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_reject_empty_message():
    response = client.post(
        "/tickets",
        json={
            "patient_name": "Demo Patient",
            "message": ""
        }
    )

    assert response.status_code == 422

def test_create_ticket():
    tickets.clear()

    response = client.post(
        "/tickets",
        json={
            "patient_name": "Demo Patient",
            "message": "I want to book an appointment"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["category"] == "appointment"
    assert data["assigned_team"] == "reception"
    assert data["status"] == "new"

    tickets.clear()
def test_ticket_is_persisted_in_memory():
    tickets.clear()

    response = client.post(
        "/tickets",
        json={
            "patient_name": "Demo Patient",
            "message": "I need an invoice"
        }
    )

    ticket_id = response.json()["id"]

    list_response = client.get("/tickets")

    assert list_response.status_code == 200
    assert any(
        ticket["id"] == ticket_id
        for ticket in list_response.json()
    )

    tickets.clear()

def test_negated_chest_pain_requires_review():
    result = classify_ticket(
        "I am not having chest pain anymore."
    )

    assert result["requires_human_review"] is True