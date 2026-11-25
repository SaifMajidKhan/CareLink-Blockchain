from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db

from backend.app.models.medication_event import (
    MedicationEvent
)

from backend.app.schemas.medication import (
    MedicationCreate,
    MedicationResponse,
    MedicationWithAnchor,
    AnchorResponse,
    IntegrityResponse
)

from backend.app.services.medication_service import (
    create_medication,
    verify_medication
)

from backend.app.services.anchor_service import (
    find_anchor,
    submit_anchor
)


router = APIRouter(
    prefix="/medications",
    tags=["Medications"]
)


def get_medication_or_404(
    medication_id: int,
    db: Session
):

    medication = db.get(
        MedicationEvent,
        medication_id
    )

    if medication is None:

        raise HTTPException(
            status_code=404,
            detail="Medication record not found"
        )

    return medication


@router.post(
    "/",
    response_model=MedicationWithAnchor,
    status_code=status.HTTP_201_CREATED
)
def register_medication(
    payload: MedicationCreate,
    db: Session = Depends(get_db)
):

    try:

        medication, anchor = create_medication(
            db,
            payload
        )

    except LookupError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    return {
        "medication": medication,
        "blockchain": anchor
    }


@router.get(
    "/",
    response_model=list[MedicationResponse]
)
def list_medications(
    patient_id: int | None = Query(
        default=None,
        gt=0
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db)
):

    statement = select(MedicationEvent)

    if patient_id is not None:

        statement = statement.where(
            MedicationEvent.patient_id == patient_id
        )

    statement = (
        statement
        .order_by(MedicationEvent.id.desc())
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get(
    "/{medication_id}",
    response_model=MedicationWithAnchor
)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_db)
):

    medication = get_medication_or_404(
        medication_id,
        db
    )

    anchor = find_anchor(
        db,
        "medication_event",
        medication.id,
        medication.version
    )

    if anchor is None:

        raise HTTPException(
            status_code=404,
            detail="Blockchain anchor not found"
        )

    return {
        "medication": medication,
        "blockchain": anchor
    }


@router.get(
    "/{medication_id}/integrity",
    response_model=IntegrityResponse
)
def check_medication_integrity(
    medication_id: int,
    db: Session = Depends(get_db)
):

    medication = get_medication_or_404(
        medication_id,
        db
    )

    return verify_medication(
        db,
        medication
    )


@router.post(
    "/{medication_id}/retry-anchor",
    response_model=AnchorResponse
)
def retry_medication_anchor(
    medication_id: int,
    db: Session = Depends(get_db)
):

    medication = get_medication_or_404(
        medication_id,
        db
    )

    anchor = find_anchor(
        db,
        "medication_event",
        medication.id,
        medication.version
    )

    if anchor is None:

        raise HTTPException(
            status_code=404,
            detail="Blockchain anchor not found"
        )

    return submit_anchor(
        db,
        anchor.id
    )