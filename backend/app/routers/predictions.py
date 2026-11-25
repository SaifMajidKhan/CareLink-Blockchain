import logging

from fastapi import APIRouter, HTTPException

from backend.app.schemas.prediction import (
    PredictionFeatures,
    PredictionResult
)

from backend.app.services.prediction_service import (
    predict_adherence_risk
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predictions",
    tags=["AI Predictions"]
)


@router.post(
    "/preview",
    response_model=PredictionResult
)
def preview_prediction(
    payload: PredictionFeatures
):

    try:

        return predict_adherence_risk(
            payload
        )

    except Exception:

        logger.exception(
            "AI prediction failed"
        )

        raise HTTPException(
            status_code=503,
            detail="AI prediction service unavailable"
        )