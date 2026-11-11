
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
    # Step 1: Apply deterministic classification.
    fallback = classify_ticket(message)

    # Step 2: Preserve recognized emergency escalation.
    if fallback["category"] == "potential_emergency":
        return {
            **fallback,
            "classification_source": "safety_rule",
        }

    # Step 3: Classify other messages using OpenAI.
    try:
        ai_result = classify_with_openai(message)
        category = ai_result.category

        # Step 4: Enforce priority and routing in Python.
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
            "classification_source": "openai",
        }

    except (OpenAIError, RuntimeError, ValueError, KeyError) as exc:
        # Don't log patient messages or API credentials.
        logger.warning(
            "AI classification failed; using fallback: %s",
            type(exc).__name__,
        )

        if fallback["category"] == "general":
            return {
                **fallback,
                "priority": "high",
                "requires_human_review": True,
                "classification_source": "fallback",
            }

        return {
            **fallback,
            "classification_source": "fallback",
        }
