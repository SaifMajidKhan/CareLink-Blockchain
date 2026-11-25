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
from backend.app.models.patient import Patient

from backend.app.schemas.patient import (
    PatientCreate,
    PatientResponse
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db)
):

    patient = Patient(
        **payload.model_dump()
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


@router.get(
    "/",
    response_model=list[PatientResponse]
)
def list_patients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db)
):

    statement = (
        select(Patient)
        .order_by(Patient.id)
        .offset(skip)
        .limit(limit)
    )

    patients = db.scalars(statement).all()

    return patients


@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):

    patient = db.get(Patient, patient_id)

    if patient is None:

        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient