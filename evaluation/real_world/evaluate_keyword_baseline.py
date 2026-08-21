import pandas as pd
from collections import Counter


DATASET_FILE = "evaluation/real_world/real_world_benchmark.csv"


KEYWORDS = {
    "authentication": [
        "unauthorized",
        "authentication",
        "invalid api key",
        "permission denied",
        "access denied",
        "401",
        "403",
    ],
    "dependency": [
        "eresolve",
        "dependency",
        "peer dependency",
        "could not resolve dependency",
        "dependency tree",
    ],
    "network": [
        "network error",
        "connection refused",
        "timeout",
        "timed out",
        "connection reset",
        "dns",
    ],
    "file": [
        "file not found",
        "no such file",
        "cannot find module",
        "enoent",
        "not found",
    ],
    "build": [
        "build failed",
        "compilation failed",
        "compile error",
        "build error",
        "failed to build",
    ],
    "test": [
        "test failed",
        "tests failed",
        "assertionerror",
        "failed test",
    ],
}


def predict(log_text):
    text = str(log_text).lower()

    scores = {}

    for category, keywords in KEYWORDS.items():
        scores[category] = sum(
            1 for keyword in keywords if keyword in text
        )

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "unknown"

    return best_category


def main():
    df = pd.read_csv(DATASET_FILE)

    total = len(df)
    correct = 0
    results = []

    for _, row in df.iterrows():
        predicted = predict(row["error_message"])
        expected = row["expected_type"]

        is_correct = predicted == expected
        correct += is_correct

        results.append(
            {
                "id": row["id"],
                "expected": expected,
                "predicted": predicted,
                "correct": is_correct,
            }
        )

        print(
            f"{row['id']}: "
            f"expected={expected} "
            f"predicted={predicted}"
        )

    accuracy = (correct / total * 100) if total else 0

    print("\n--- Real-World Keyword Baseline ---")
    print(f"Total cases: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")

    failures = [r for r in results if not r["correct"]]

    print(f"\nFailures: {len(failures)}")

    print("\nFailures by expected type:")
    print(Counter(r["expected"] for r in failures))

    print("\nPrediction errors:")
    print(
        Counter(
            (r["expected"], r["predicted"])
            for r in failures
        )
    )


if __name__ == "__main__":
    main()
