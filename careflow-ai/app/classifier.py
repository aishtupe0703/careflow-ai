
def classify_ticket(message: str) -> dict:
    text = message.lower()

    emergency_phrases = [
        "chest pain",
        "difficulty breathing",
        "unconscious",
        "severe bleeding",
    ]

    if any(term in text for term in emergency_phrases):
        return {
            "category": "potential_emergency",
            "priority": "critical",
            "assigned_team": "emergency_escalation",
            "requires_human_review": True,
        }

    if any(word in text for word in ["appointment", "reschedule", "booking"]):
        category, team = "appointment", "reception"
    elif any(word in text for word in ["payment", "refund", "invoice"]):
        category, team = "billing", "billing"
    elif any(word in text for word in ["report", "lab result"]):
        category, team = "medical_records", "authorized_records_staff"
    else:
        category, team = "general", "front_desk"

    return {
        "category": category,
        "priority": "normal",
        "assigned_team": team,
        "requires_human_review": True,
    }
