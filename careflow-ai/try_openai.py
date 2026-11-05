
from app.services.openai_classifier import classify_with_openai

message = (
    "Hello, I would like to reschedule "
    "my dermatology appointment to Friday."
)

result = classify_with_openai(message)

print(result.model_dump_json(indent=2))
