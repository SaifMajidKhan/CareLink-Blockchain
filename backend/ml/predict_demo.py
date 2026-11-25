from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "artifacts"
    / "adherence_model.joblib"
)


def classify_risk(probability):

    if probability < 0.30:
        return "Low"

    if probability < 0.70:
        return "Medium"

    return "High"


def main():

    model = joblib.load(
        MODEL_PATH
    )

    patients = pd.DataFrame([
        {
            "age": 45,
            "daily_doses": 1,
            "missed_doses_7d": 0,
            "adherence_rate_30d": 0.98,
            "reminder_response_rate": 0.95,
            "medication_count": 1,
            "chronic_condition_count": 1,
            "previous_non_adherence": 0
        },
        {
            "age": 58,
            "daily_doses": 2,
            "missed_doses_7d": 4,
            "adherence_rate_30d": 0.72,
            "reminder_response_rate": 0.60,
            "medication_count": 3,
            "chronic_condition_count": 1,
            "previous_non_adherence": 1
        },
        {
            "age": 62,
            "daily_doses": 4,
            "missed_doses_7d": 18,
            "adherence_rate_30d": 0.40,
            "reminder_response_rate": 0.20,
            "medication_count": 6,
            "chronic_condition_count": 3,
            "previous_non_adherence": 1
        }
    ])

    probabilities = model.predict_proba(
        patients
    )[:, 1]

    print("CareLink AI Risk Prediction Demo")
    print("=" * 45)

    for index, probability in enumerate(
        probabilities,
        start=1
    ):

        print(f"\nDemo Patient {index:03}")

        print(
            f"Risk score: {probability * 100:.2f}%"
        )

        print(
            f"Risk level: {classify_risk(probability)}"
        )

    print(
        "\nSynthetic demonstration only."
    )

    print(
        "Not a clinically validated prediction."
    )


if __name__ == "__main__":
    main()