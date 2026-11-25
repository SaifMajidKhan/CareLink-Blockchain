import hashlib
import json
import math

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
import sklearn

from backend.app.schemas.prediction import (
    PredictionFeatures
)


BASE_DIR = Path(__file__).resolve().parents[2]

ARTIFACT_DIR = BASE_DIR / "ml" / "artifacts"

MODEL_PATH = (
    ARTIFACT_DIR / "adherence_model.joblib"
)

METADATA_PATH = (
    ARTIFACT_DIR / "model_metadata.json"
)

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


@lru_cache(maxsize=1)
def load_prediction_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "Trained AI model not found"
        )

    if not METADATA_PATH.exists():

        raise FileNotFoundError(
            "AI model metadata not found"
        )

    metadata = json.loads(
        METADATA_PATH.read_text(
            encoding="utf-8"
        )
    )

    actual_hash = hashlib.sha256(
        MODEL_PATH.read_bytes()
    ).hexdigest()

    if actual_hash != metadata["model_sha256"]:

        raise RuntimeError(
            "AI model fingerprint mismatch"
        )

    if metadata["features"] != FEATURES:

        raise RuntimeError(
            "AI model feature configuration mismatch"
        )

    if (
        metadata["sklearn_version"]
        != sklearn.__version__
    ):

        raise RuntimeError(
            "Scikit-learn version mismatch"
        )

    # Only load locally generated, trusted artifacts.
    model = joblib.load(MODEL_PATH)

    if list(model.feature_names_in_) != FEATURES:

        raise RuntimeError(
            "Trained model feature mismatch"
        )

    if list(model.classes_) != [0, 1]:

        raise RuntimeError(
            "Unexpected model output classes"
        )

    return model, metadata


def classify_risk(risk_score: float) -> str:

    if risk_score < 30:
        return "Low"

    if risk_score < 70:
        return "Medium"

    return "High"


def predict_adherence_risk(
    features: PredictionFeatures
) -> dict:

    model, metadata = load_prediction_model()

    dataframe = pd.DataFrame(
        [features.model_dump()],
        columns=FEATURES
    )

    probability = float(
        model.predict_proba(dataframe)[0][1]
    )

    if (
        not math.isfinite(probability)
        or not 0 <= probability <= 1
    ):

        raise RuntimeError(
            "Invalid model probability"
        )

    risk_score = round(
        probability * 100,
        2
    )

    return {
        "risk_score": risk_score,
        "risk_level": classify_risk(risk_score),
        "model_version": metadata["model_version"],
        "model_sha256": metadata["model_sha256"],
        "algorithm": metadata["algorithm"],
        "dataset_type": metadata["dataset_type"],
        "disclaimer": (
            "Synthetic-data demonstration only. "
            "Not clinically validated."
        )
    }