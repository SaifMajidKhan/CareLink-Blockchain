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
from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db

from backend.app.models.ai_prediction import AIPrediction

from backend.app.schemas.prediction import PredictionCreate

from backend.app.services.anchor_service import (
    find_anchor,
    submit_anchor
)

from backend.app.services.prediction_record_service import (
    create_prediction,
    verify_prediction,
    serialize_prediction,
    serialize_prediction_anchor
)


@router.post("/", status_code=201)
def register_prediction(
    payload: PredictionCreate,
    db: Session = Depends(get_db)
):

    try:

        prediction, anchor = create_prediction(
            db,
            payload
        )

        return {
            "prediction": serialize_prediction(
                prediction
            ),
            "blockchain": serialize_prediction_anchor(
                anchor
            )
        }

    except LookupError as exc:

        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception:

        db.rollback()

        logger.exception(
            "Prediction registration failed"
        )

        raise HTTPException(
            status_code=503,
            detail="Prediction registration unavailable"
        )


@router.get("/")
def list_predictions(
    patient_id: int | None = None,
    db: Session = Depends(get_db)
):

    statement = select(AIPrediction)

    if patient_id is not None:

        statement = statement.where(
            AIPrediction.patient_id == patient_id
        )

    statement = statement.order_by(
        AIPrediction.id.desc()
    )

    predictions = db.scalars(statement).all()

    return [
        {
            "prediction": serialize_prediction(item),
            "blockchain": serialize_prediction_anchor(
                find_anchor(
                    db,
                    "ai_prediction",
                    item.id,
                    item.version
                )
            )
        }
        for item in predictions
    ]


@router.get("/{prediction_id}")
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):

    prediction = db.get(
        AIPrediction,
        prediction_id
    )

    if prediction is None:

        raise HTTPException(
            status_code=404,
            detail="Prediction not found"
        )

    anchor = find_anchor(
        db,
        "ai_prediction",
        prediction.id,
        prediction.version
    )

    return {
        "prediction": serialize_prediction(
            prediction
        ),
        "blockchain": serialize_prediction_anchor(
            anchor
        )
    }


@router.get("/{prediction_id}/integrity")
def prediction_integrity(
    prediction_id: int,
    db: Session = Depends(get_db)
):

    prediction = db.get(
        AIPrediction,
        prediction_id
    )

    if prediction is None:

        raise HTTPException(
            status_code=404,
            detail="Prediction not found"
        )

    return verify_prediction(
        db,
        prediction
    )


@router.post("/{prediction_id}/retry-anchor")
def retry_prediction_anchor(
    prediction_id: int,
    db: Session = Depends(get_db)
):

    prediction = db.get(
        AIPrediction,
        prediction_id
    )

    if prediction is None:

        raise HTTPException(
            status_code=404,
            detail="Prediction not found"
        )

    anchor = find_anchor(
        db,
        "ai_prediction",
        prediction.id,
        prediction.version
    )

    if anchor is None:

        raise HTTPException(
            status_code=404,
            detail="Prediction anchor not found"
        )

    anchor = submit_anchor(
        db,
        anchor.id
    )

    return serialize_prediction_anchor(
        anchor
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