
import time
import csv
from datetime import datetime, timezone
from pathlib import Path

from app.services.classification_service import classify_for_ticket
from evals.test_cases import TEST_CASES


def run_evaluation():
    correct = 0
    total = len(TEST_CASES)
    results = []

    if total == 0:
        print("No evaluation cases found.")
        return

    for index, case in enumerate(TEST_CASES, start=1):
        start = time.perf_counter()

        result = classify_for_ticket(case["message"])

        latency = time.perf_counter() - start

        predicted = result["category"]
        expected = case["expected_category"]
        passed = predicted == expected

        if passed:
            correct += 1

        results.append({
            "expected": expected,
            "predicted": predicted,
            "passed": passed,
            "latency": latency,
            "source": result.get(
                "classification_source", "unknown"
            ),
        })

        print(
            f"{index}. "
            f"Expected={expected}, "
            f"Predicted={predicted}, "
            f"Match={passed}, "
            f"Source={results[-1]['source']}, "
            f"Latency={latency:.2f}s"
        )

    # 1. Overall accuracy
    accuracy = correct / total * 100

    # 2. Average latency
    average_latency = sum(
        r["latency"] for r in results
    ) / total

    # 3. Emergency recall
    emergencies = [
        r for r in results
        if r["expected"] == "potential_emergency"
    ]

    detected = sum(
        r["predicted"] == "potential_emergency"
        for r in emergencies
    )

    emergency_recall = (
        detected / len(emergencies)
        if emergencies else None
    )

    # 4. Classification source counts
    source_counts = {}

    for r in results:
        source = r["source"]
        source_counts[source] = (
            source_counts.get(source, 0) + 1
        )

    output_dir = Path("evals/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"evaluation_{timestamp}.csv"

    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "expected",
                "predicted",
                "passed",
                "latency",
                "source",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {output_file}")

    # 5. Final report
    print("\n===== CareFlow AI Evaluation =====")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Correct: {correct}/{total}")
    print(f"Average latency: {average_latency:.2f}s")

    if emergency_recall is not None:
        print(f"Emergency recall: {emergency_recall:.1%}")
    else:
        print("Emergency recall: N/A (no emergency cases)")

    print("\nClassification sources:")
    for source, count in source_counts.items():
        print(f"  {source}: {count}")

    return results


if __name__ == "__main__":
    run_evaluation()
