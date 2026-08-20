import json
import os
import time

import requests


API_URL = "http://127.0.0.1:5000/analyze"
DATASET_DIR = "evaluation/dataset"
LABELS_FILE = "evaluation/labels.json"
RESULTS_FILE = "evaluation/results.json"


def load_labels():
    with open(LABELS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def find_log_file(filename):
    for root, _, files in os.walk(DATASET_DIR):
        if filename in files:
            return os.path.join(root, filename)

    raise FileNotFoundError(f"Could not find {filename}")


def analyze_log(log_text):
    start = time.perf_counter()

    response = requests.post(
        API_URL,
        json={"logs": log_text},
        timeout=60,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    response.raise_for_status()

    payload = response.json()

    analysis = payload["data"]["analysis"]

    return analysis, elapsed_ms


def main():
    labels = load_labels()

    results = []

    for filename, expected_type in labels.items():
        print(f"Evaluating: {filename}")

        path = find_log_file(filename)

        with open(path, "r", encoding="utf-8") as file:
            log_text = file.read()

        try:
            analysis, elapsed_ms = analyze_log(log_text)

            predicted_type = analysis.get("error_type", "unknown")

            results.append(
                {
                    "file": filename,
                    "expected": expected_type,
                    "predicted": predicted_type,
                    "correct": predicted_type == expected_type,
                    "latency_ms": round(elapsed_ms, 2),
                    "status": "success",
                }
            )

            print(
                f"  expected={expected_type} "
                f"predicted={predicted_type} "
                f"latency={elapsed_ms:.2f}ms"
            )

        except Exception as exc:
            results.append(
                {
                    "file": filename,
                    "expected": expected_type,
                    "predicted": "error",
                    "correct": False,
                    "latency_ms": None,
                    "status": "failed",
                    "error": str(exc),
                }
            )

            print(f"  FAILED: {exc}")

    total = len(results)
    correct = sum(result["correct"] for result in results)

    accuracy = (correct / total * 100) if total else 0

    successful_latencies = [
        result["latency_ms"]
        for result in results
        if result["latency_ms"] is not None
    ]

    average_latency = (
        sum(successful_latencies) / len(successful_latencies)
        if successful_latencies
        else 0
    )

    summary = {
        "total_cases": total,
        "correct_cases": correct,
        "accuracy_percent": round(accuracy, 2),
        "average_latency_ms": round(average_latency, 2),
        "results": results,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print("\n--- Evaluation Summary ---")
    print(f"Total cases: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Average latency: {average_latency:.2f} ms")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()