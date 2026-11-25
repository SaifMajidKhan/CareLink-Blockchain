import pytest

from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.main import app

from backend.app.schemas.prediction import (
    PredictionFeatures
)

from backend.app.services.prediction_service import (
    classify_risk,
    load_prediction_model,
    predict_adherence_risk
)


client = TestClient(app)


LOW_RISK = {
    "age": 45,
    "daily_doses": 1,
    "missed_doses_7d": 0,
    "adherence_rate_30d": 0.98,
    "reminder_response_rate": 0.95,
    "medication_count": 1,
    "chronic_condition_count": 1,
    "previous_non_adherence": 0
}


HIGH_RISK = {
    "age": 62,
    "daily_doses": 4,
    "missed_doses_7d": 18,
    "adherence_rate_30d": 0.40,
    "reminder_response_rate": 0.20,
    "medication_count": 6,
    "chronic_condition_count": 3,
    "previous_non_adherence": 1
}


def test_model_loading():

    model, metadata = load_prediction_model()

    assert model is not None

    assert metadata["model_version"] == (
        "carelink-logreg-v1"
    )


def test_valid_prediction_features():

    features = PredictionFeatures(**LOW_RISK)

    assert features.age == 45

    assert features.daily_doses == 1


def test_invalid_age():

    data = {
        **LOW_RISK,
        "age": -5
    }

    with pytest.raises(ValidationError):

        PredictionFeatures(**data)


def test_invalid_adherence_rate():

    data = {
        **LOW_RISK,
        "adherence_rate_30d": 1.5
    }

    with pytest.raises(ValidationError):

        PredictionFeatures(**data)


def test_invalid_missed_doses():

    data = {
        **LOW_RISK,
        "missed_doses_7d": 20
    }

    with pytest.raises(ValidationError):

        PredictionFeatures(**data)


def test_risk_classification():

    assert classify_risk(0) == "Low"

    assert classify_risk(29.99) == "Low"

    assert classify_risk(30) == "Medium"

    assert classify_risk(69.99) == "Medium"

    assert classify_risk(70) == "High"

    assert classify_risk(100) == "High"


def test_prediction_score_range():

    features = PredictionFeatures(**LOW_RISK)

    result = predict_adherence_risk(features)

    assert 0 <= result["risk_score"] <= 100


def test_prediction_determinism():

    features = PredictionFeatures(**LOW_RISK)

    first = predict_adherence_risk(features)

    second = predict_adherence_risk(features)

    assert first == second


def test_high_risk_exceeds_low_risk():

    low = predict_adherence_risk(
        PredictionFeatures(**LOW_RISK)
    )

    high = predict_adherence_risk(
        PredictionFeatures(**HIGH_RISK)
    )

    assert high["risk_score"] > low["risk_score"]


def test_prediction_api():

    response = client.post(
        "/predictions/preview",
        json=LOW_RISK
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_level"] == "Low"

    assert data["dataset_type"] == "synthetic"

    assert len(data["model_sha256"]) == 64


def test_prediction_api_invalid_input():

    response = client.post(
        "/predictions/preview",
        json={
            **LOW_RISK,
            "missed_doses_7d": 20
        }
    )

    assert response.status_code == 422


def test_prediction_service_unavailable(
    monkeypatch
):

    def unavailable_model(payload):

        raise RuntimeError(
            "Model unavailable"
        )

    monkeypatch.setattr(
        "backend.app.routers.predictions."
        "predict_adherence_risk",
        unavailable_model
    )

    response = client.post(
        "/predictions/preview",
        json=LOW_RISK
    )

    assert response.status_code == 503