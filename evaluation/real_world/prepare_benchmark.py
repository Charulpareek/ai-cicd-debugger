import pandas as pd


INPUT_FILE = "cicd_real_ood_world_dataset.csv"
OUTPUT_FILE = "real_world_benchmark.csv"

CATEGORY_MAP = {
    "Authentication": "authentication",
    "Dependencies": "dependency",
    "Network": "network",
    "Test": "test",
    "Build": "build",
}


def main():
    df = pd.read_csv(INPUT_FILE)

    selected = df[df["category"].isin(CATEGORY_MAP)].copy()

    benchmark = selected[
        [
            "id",
            "category",
            "error_message",
            "source_url",
        ]
    ].copy()

    benchmark["expected_type"] = benchmark["category"].map(CATEGORY_MAP)

    # Keep only the fields needed for evaluation.
    benchmark = benchmark[
        [
            "id",
            "error_message",
            "expected_type",
            "category",
            "source_url",
        ]
    ]

    # Remove rows without an actual error message.
    benchmark = benchmark.dropna(subset=["error_message"])

    # Remove exact duplicate error messages.
    benchmark = benchmark.drop_duplicates(
        subset=["error_message"]
    )

    benchmark.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print("--- Real-World Benchmark ---")
    print(f"Cases: {len(benchmark)}")
    print("\nCategories:")
    print(benchmark["expected_type"].value_counts())
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()