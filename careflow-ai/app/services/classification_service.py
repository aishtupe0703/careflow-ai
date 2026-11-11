
import logging
import time
from openai import OpenAIError

from app.classifier import classify_ticket
from app.services.openai_classifier import classify_with_openai

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
logger = logging.getLogger("uvicorn.error")

TEAM_BY_CATEGORY = {
    "appointment": "reception",
    "billing": "billing",
    "medical_records": "authorized_records_staff",
    "general": "front_desk",
    "potential_emergency": "emergency_escalation",
}


def record_classification(result: dict, started: float) -> dict:
    latency_ms = round(
        (time.perf_counter() - started) * 1000,
        2,
    )

    result = {
        **result,
        "latency_ms": latency_ms,
    }

    logger.info(
        "classification_completed source=%s category=%s "
        "priority=%s latency_ms=%.2f",
        result["classification_source"],
        result["category"],
        result["priority"],
        latency_ms,
    )

    return result



def classify_for_ticket(message: str) -> dict:
    started = time.perf_counter()
    # Step 1: Apply deterministic classification.
    fallback = classify_ticket(message)

    # Step 2: Preserve recognized emergency escalation.
    if fallback["category"] == "potential_emergency":
        return record_classification(
        {
            **fallback,
            "classification_source": "safety_rule",
        },
        started,
    )

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

        return record_classification(
            {
                "category": category,
                "priority": priority,
                "assigned_team": TEAM_BY_CATEGORY[category],
                "requires_human_review": True,
                "classification_source": "openai",
            },
            started,
        )
    

    
    except (OpenAIError, RuntimeError, ValueError, KeyError) as exc:
        logger.warning(
            "AI classification failed; using fallback: %s",
            type(exc).__name__,
        )

        if fallback["category"] == "general":
            fallback = {
                **fallback,
                "priority": "high",
                "requires_human_review": True,
            }

        return record_classification(
            {
                **fallback,
                "classification_source": "fallback",
            },
            started,
        )
