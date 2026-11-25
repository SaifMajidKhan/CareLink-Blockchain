from copy import deepcopy
from datetime import datetime, timezone

import pytest

from backend.app.models.ai_prediction import AIPrediction

from backend.app.services.prediction_record_service import (
    build_prediction_payload
)

from blockchain.services.hashing_service import (
    generate_fingerprint,
    generate_salt
)


@pytest.fixture
def prediction():

    return AIPrediction(
        id=1,
        patient_id=1,
        record_ref="0x" + "a" * 64,
        version=1,
        input_features={
            "age": 45,
            "daily_doses": 2,
            "missed_doses_7d": 5,
            "adherence_rate_30d": 0.65,
            "reminder_response_rate": 0.40,
            "medication_count": 2,
            "chronic_condition_count": 1,
            "previous_non_adherence": 1
        },
        risk_score_bps=8500,
        risk_level="High",
        model_version="carelink-logreg-v1",
        model_sha256="a" * 64,
        algorithm="Logistic Regression",
        dataset_type="synthetic",
        created_at=datetime(
            2026, 11, 25,
            tzinfo=timezone.utc
        )
    )


def test_prediction_fingerprint_determinism(
    prediction
):

    salt = generate_salt()

    first = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    second = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    assert first == second


@pytest.mark.parametrize(
    "field,new_value",
    [
        ("risk_score_bps", 1500),
        ("risk_level", "Low"),
        ("model_version", "modified-model"),
        ("model_sha256", "b" * 64),
        ("patient_id", 2),
        ("algorithm", "Random Forest"),
        ("dataset_type", "modified"),
        ("record_ref", "0x" + "b" * 64),
        (
            "created_at",
            datetime(
                2026, 11, 26,
                tzinfo=timezone.utc
            )
        )
    ]
)
def test_prediction_field_tampering(
    prediction,
    field,
    new_value
):

    salt = generate_salt()

    original = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    setattr(
        prediction,
        field,
        new_value
    )

    modified = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    assert original != modified


def test_prediction_input_tampering(
    prediction
):

    salt = generate_salt()

    original = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    modified_features = deepcopy(
        prediction.input_features
    )

    modified_features["missed_doses_7d"] = 0

    prediction.input_features = modified_features

    modified = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    assert original != modified


def test_prediction_restoration(
    prediction
):

    salt = generate_salt()

    original = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    prediction.risk_score_bps = 1500

    modified = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    prediction.risk_score_bps = 8500

    restored = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    assert original != modified

    assert original == restored