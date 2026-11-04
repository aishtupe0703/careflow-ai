
from fastapi.testclient import TestClient
from app.main import app, tickets

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


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
