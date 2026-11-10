
TEST_CASES = [
    {
        "message": "Please reschedule my appointment to Friday.",
        "expected_category": "appointment",
    },
    {
        "message": "I need a refund for my consultation.",
        "expected_category": "billing",
    },
    {
        "message": "How do I obtain a copy of my lab report?",
        "expected_category": "medical_records",
    },
    {
        "message": "What time does the clinic close?",
        "expected_category": "general",
    },
    {
        "message": "My father has severe chest pain.",
        "expected_category": "potential_emergency",
    },
    {
        "message": "There is a charge I do not recognize.",
        "expected_category": "billing",
    },
    {
        "message": "Could I move my consultation to next week?",
        "expected_category": "appointment",
    },
    {
        "message": "My mother suddenly became confused and weak.",
        "expected_category": "potential_emergency",
    },
]
