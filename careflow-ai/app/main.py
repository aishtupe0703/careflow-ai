from fastapi import FastAPI
from pydantic import BaseModel, Field
from uuid import uuid4

app = FastAPI(title="CareFlow AI")

class TicketCreate(BaseModel):
    patient_name: str = Field(min_length=1)
    message: str = Field(min_length=1)

tickets = {}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/tickets", status_code=201)
def create_ticket(ticket: TicketCreate):
    ticket_id = str(uuid4())

    new_ticket = {
        "id": ticket_id,
        "patient_name": ticket.patient_name,
        "message": ticket.message,
        "status": "new"
    }

    tickets[ticket_id] = new_ticket
    return new_ticket

@app.get("/tickets")
def list_tickets():
    return list(tickets.values())
