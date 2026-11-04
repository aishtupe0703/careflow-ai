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