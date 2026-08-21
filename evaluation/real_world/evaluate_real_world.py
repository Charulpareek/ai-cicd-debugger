import argparse
import json
import os
import sys
import time

import pandas as pd
import requests


API_URL = "http://127.0.0.1:5000/analyze"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_DATASET = os.path.join(
    SCRIPT_DIR,
    "dev.csv",
)

DEFAULT_RESULTS = os.path.join(
    SCRIPT_DIR,
    "dev_results.json",
)


def normalize_label(label):
    label = str(label).strip().lower()

    aliases = {
        "authentication": "authentication",
        "auth": "authentication",
        "dependency": "dependency",
        "dependencies": "dependency",
        "network": "network",
        "test": "test",
        "testing": "test",
        "build": "build",
    }

    return aliases.get(label, label)


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
    parser = argparse.ArgumentParser(
        description="Evaluate the CI/CD classifier on a benchmark."
    )

    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help="Path to benchmark CSV",
    )

    parser.add_argument(
        "--results",
        default=DEFAULT_RESULTS,
        help="Path to save evaluation results",
    )

    args = parser.parse_args()

    dataset_file = os.path.abspath(args.dataset)
    results_file = os.path.abspath(args.results)

    if not os.path.exists(dataset_file):
        print(f"ERROR: dataset not found:")
        print(dataset_file)
        sys.exit(1)

    df = pd.read_csv(dataset_file)

    print("--- CI/CD Evaluation ---")
    print(f"Dataset: {dataset_file}")
    print(f"Cases: {len(df)}")
    print()

    print("Categories:")
    print(df["expected_type"].value_counts())
    print()

    results = []

    for _, row in df.iterrows():
        case_id = row["id"]

        expected = normalize_label(
            row["expected_type"]
        )

        error_message = str(
            row["error_message"]
        )

        print(f"Evaluating: {case_id}")

        try:
            analysis, latency_ms = analyze_log(
                error_message
            )

            predicted = normalize_label(
                analysis.get(
                    "error_type",
                    "unknown",
                )
            )

            correct = predicted == expected

            results.append(
                {
                    "id": case_id,
                    "expected": expected,
                    "predicted": predicted,
                    "correct": correct,
                    "latency_ms": round(
                        latency_ms,
                        2,
                    ),
                    "status": "success",
                }
            )

            print(
                f"  expected={expected} "
                f"predicted={predicted} "
                f"correct={correct} "
                f"latency={latency_ms:.2f}ms"
            )

        except Exception as exc:
            results.append(
                {
                    "id": case_id,
                    "expected": expected,
                    "predicted": "error",
                    "correct": False,
                    "latency_ms": None,
                    "status": "failed",
                    "error": str(exc),
                }
            )

            print(
                f"  FAILED: {exc}"
            )

    total = len(results)

    correct = sum(
        result["correct"]
        for result in results
    )

    accuracy = (
        correct / total * 100
        if total
        else 0
    )

    successful = [
        result
        for result in results
        if result["status"] == "success"
    ]

    latencies = [
        result["latency_ms"]
        for result in successful
        if result["latency_ms"] is not None
    ]

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else 0
    )

    summary = {
        "benchmark": os.path.basename(
            dataset_file
        ),
        "total_cases": total,
        "correct_cases": correct,
        "accuracy_percent": round(
            accuracy,
            2,
        ),
        "average_latency_ms": round(
            average_latency,
            2,
        ),
        "results": results,
    }

    os.makedirs(
        os.path.dirname(results_file),
        exist_ok=True,
    )

    with open(
        results_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )

    print()
    print("--- Evaluation Summary ---")
    print(f"Total cases: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(
        f"Average latency: "
        f"{average_latency:.2f} ms"
    )
    print(
        f"Results saved to: "
        f"{results_file}"
    )


if __name__ == "__main__":
    main()