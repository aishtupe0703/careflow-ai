
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.classifier import classify_ticket
from app.database import get_db
from app.models import Ticket

from typing import Callable

from app.services.classification_service import classify_for_ticket

app = FastAPI(title="CareFlow AI")
def get_ticket_classifier() -> Callable[[str], dict]:
    return classify_for_ticket

class TicketCreate(BaseModel):
    patient_name: str = Field(min_length=1)
    message: str = Field(min_length=1)


def serialize_ticket(ticket: Ticket) -> dict:
    return {
        "id": ticket.id,
        "patient_name": ticket.patient_name,
        "message": ticket.message,
        "status": ticket.status,
        "category": ticket.category,
        "priority": ticket.priority,
        "assigned_team": ticket.assigned_team,
        "requires_human_review": ticket.requires_human_review,
        "created_at": ticket.created_at.isoformat(),
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/tickets", status_code=201)
def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    classifier: Callable[[str], dict] = Depends(
        get_ticket_classifier
    ),
):
    classification = classifier(ticket.message)
    
    new_ticket = Ticket(
        patient_name=ticket.patient_name,
        message=ticket.message,
        category=classification["category"],
        priority=classification["priority"],
        assigned_team=classification["assigned_team"],
        requires_human_review=classification[
            "requires_human_review"
        ],
        status="new",
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return serialize_ticket(new_ticket)


@app.get("/tickets")
def list_tickets(db: Session = Depends(get_db)):
    result = db.execute(select(Ticket))
    saved_tickets = result.scalars().all()

    return [serialize_ticket(ticket) for ticket in saved_tickets]
