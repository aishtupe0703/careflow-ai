
import logging

from openai import OpenAIError

from app.classifier import classify_ticket
from app.services.openai_classifier import classify_with_openai

logger = logging.getLogger(__name__)

TEAM_BY_CATEGORY = {
    "appointment": "reception",
    "billing": "billing",
    "medical_records": "authorized_records_staff",
    "general": "front_desk",
    "potential_emergency": "emergency_escalation",
}


def classify_for_ticket(message: str) -> dict:
    # Step 1: Apply existing deterministic rules.
    fallback = classify_ticket(message)

    # Step 2: Preserve recognized emergency escalation.
    if fallback["category"] == "potential_emergency":
        return fallback

    # Step 3: Ask OpenAI to classify other messages.
    try:
        ai_result = classify_with_openai(message)

        category = ai_result.category

        # Step 4: Enforce routing rules in Python.
        priority = (
            "critical"
            if category == "potential_emergency"
            else ai_result.priority
        )

        if category != "potential_emergency":
            priority = (
                priority if priority in ("normal", "high")
                else "high"
            )

        return {
            "category": category,
            "priority": priority,
            "assigned_team": TEAM_BY_CATEGORY[category],
            "requires_human_review": True,
        }

    except (OpenAIError, RuntimeError, ValueError, KeyError) as exc:
        # Do not log the patient message or API credentials.
        logger.warning(
            "AI classification failed; using fallback: %s",
            type(exc).__name__,
        )
        return fallback
