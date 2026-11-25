import hashlib
import json

from pathlib import Path

import joblib
import pandas as pd
import sklearn

from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split

from sklearn.pipeline import Pipeline

from sklearn.preprocessing import StandardScaler

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "medication_adherence.csv"
)

ARTIFACT_DIR = BASE_DIR / "artifacts"

MODEL_VERSION = "carelink-logreg-v1"

FEATURES = [
    "age",
    "daily_doses",
    "missed_doses_7d",
    "adherence_rate_30d",
    "reminder_response_rate",
    "medication_count",
    "chronic_condition_count",
    "previous_non_adherence"
]

TARGET = "non_adherent_next_7d"


def train_model():

    dataset = pd.read_csv(
        DATASET_PATH
    )

    X = dataset[FEATURES]
    y = dataset[TARGET]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    model = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42
            )
        )
    ])

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    metrics = {
        "model_version": MODEL_VERSION,
        "algorithm": "Logistic Regression",
        "dataset_type": "synthetic",
        "dataset_sha256": hashlib.sha256(
            DATASET_PATH.read_bytes()
        ).hexdigest(),
        "sklearn_version": sklearn.__version__,
        "total_records": len(dataset),
        "training_records": len(X_train),
        "testing_records": len(X_test),
        "features": FEATURES,
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "precision": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),
        "recall": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),
        "f1_score": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_test,
                probabilities
            )
        ),
        "confusion_matrix": confusion_matrix(
            y_test,
            predictions
        ).tolist()
    }

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    model_path = (
        ARTIFACT_DIR
        / "adherence_model.joblib"
    )

    joblib.dump(
        model,
        model_path
    )

    metrics["model_sha256"] = hashlib.sha256(
        model_path.read_bytes()
    ).hexdigest()

    metrics_path = (
        ARTIFACT_DIR
        / "model_metadata.json"
    )

    metrics_path.write_text(
        json.dumps(metrics, indent=4),
        encoding="utf-8"
    )

    print("Model trained successfully!")

    print("\nTraining records:", len(X_train))
    print("Testing records:", len(X_test))

    print("\nEvaluation metrics:")

    for metric in [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc"
    ]:

        print(
            f"{metric}: {metrics[metric]:.4f}"
        )

    print("\nConfusion matrix:")
    print(metrics["confusion_matrix"])

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    print("\nModel saved:", model_path)
    print("Metadata saved:", metrics_path)


if __name__ == "__main__":
    train_model()