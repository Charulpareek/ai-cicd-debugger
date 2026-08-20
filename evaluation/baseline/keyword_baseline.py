import json
import os


DATASET_DIR = "evaluation/dataset"
LABELS_FILE = "evaluation/labels.json"


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


def find_log_file(filename):
    for root, _, files in os.walk(DATASET_DIR):
        if filename in files:
            return os.path.join(root, filename)

    raise FileNotFoundError(filename)


def predict(log_text):
    text = log_text.lower()

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
    with open(LABELS_FILE, "r", encoding="utf-8") as file:
        labels = json.load(file)

    total = 0
    correct = 0

    for filename, expected in labels.items():
        path = find_log_file(filename)

        with open(path, "r", encoding="utf-8") as file:
            log_text = file.read()

        predicted = predict(log_text)

        total += 1
        correct += predicted == expected

        print(
            f"{filename}: "
            f"expected={expected} "
            f"predicted={predicted}"
        )

    accuracy = (correct / total * 100) if total else 0

    print("\n--- Keyword Baseline ---")
    print(f"Total cases: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")


if __name__ == "__main__":
    main()