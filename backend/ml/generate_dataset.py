from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "medication_adherence.csv"
)

RANDOM_SEED = 42
SAMPLE_COUNT = 5000


def generate_dataset():

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    age = rng.integers(
        18, 86, SAMPLE_COUNT
    )

    daily_doses = rng.integers(
        1, 5, SAMPLE_COUNT
    )

    adherence_tendency = rng.beta(
        5, 2, SAMPLE_COUNT
    )

    missed_doses_7d = rng.binomial(
        daily_doses * 7,
        1 - adherence_tendency
    )

    missed_doses_previous_23d = rng.binomial(
        daily_doses * 23,
        1 - adherence_tendency
    )

    adherence_rate_30d = (
        1 - (
            missed_doses_7d
            + missed_doses_previous_23d
        ) / (daily_doses * 30)
    )

    reminder_response_rate = np.clip(
        adherence_tendency
        + rng.normal(0, 0.15, SAMPLE_COUNT),
        0,
        1
    )

    medication_count = rng.integers(
        1, 7, SAMPLE_COUNT
    )

    chronic_condition_count = rng.integers(
        1, 4, SAMPLE_COUNT
    )

    previous_non_adherence = rng.binomial(
        1,
        1 - adherence_tendency
    )

    # Assumed relationships for simulation only.
    # These coefficients are not clinical findings.

    logits = (
        -1.8
        + 0.04 * missed_doses_7d
        + 3.5 * (1 - adherence_rate_30d)
        + 1.8 * (1 - reminder_response_rate)
        + 0.18 * (daily_doses - 1)
        + 0.10 * (medication_count - 1)
        + 0.12 * (chronic_condition_count - 1)
        + 0.65 * previous_non_adherence
        + rng.normal(0, 0.45, SAMPLE_COUNT)
    )

    probability = 1 / (
        1 + np.exp(-logits)
    )

    non_adherent_next_7d = rng.binomial(
        1,
        probability
    )

    dataset = pd.DataFrame({
        "age": age,
        "daily_doses": daily_doses,
        "missed_doses_7d": missed_doses_7d,
        "adherence_rate_30d": np.round(
            adherence_rate_30d, 4
        ),
        "reminder_response_rate": np.round(
            reminder_response_rate, 4
        ),
        "medication_count": medication_count,
        "chronic_condition_count": chronic_condition_count,
        "previous_non_adherence": previous_non_adherence,
        "non_adherent_next_7d": non_adherent_next_7d
    })

    DATASET_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataset.to_csv(
        DATASET_PATH,
        index=False
    )

    print("Dataset generated successfully!")
    print("Location:", DATASET_PATH)
    print("Shape:", dataset.shape)

    print("\nFirst five records:")
    print(dataset.head().to_string(index=False))

    print("\nMissing values:")
    print(dataset.isnull().sum())

    print("\nTarget distribution:")
    print(
        dataset["non_adherent_next_7d"]
        .value_counts()
    )

    print("\nTarget percentages:")
    print(
        dataset["non_adherent_next_7d"]
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
    )


if __name__ == "__main__":
    generate_dataset()