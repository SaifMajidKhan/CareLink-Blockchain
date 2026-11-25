import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from fastapi.responses import FileResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db

from backend.app.models.medical_report import MedicalReport

from backend.app.schemas.report import ReportCreate

from backend.app.services.anchor_service import (
    find_anchor,
    submit_anchor
)

from backend.app.services.prediction_record_service import (
    serialize_prediction_anchor
)

from backend.app.services.medical_report_service import (
    REPORT_DIR,
    create_medical_report,
    verify_medical_report,
    serialize_report
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/reports",
    tags=["Medical Reports"]
)

MAX_FILE_SIZE = 10 * 1024 * 1024


def get_report_or_404(
    db,
    report_id
):

    report = db.get(
        MedicalReport,
        report_id
    )

    if report is None:

        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report


def report_response(
    db,
    report
):

    anchor = find_anchor(
        db,
        "medical_report",
        report.id,
        report.version
    )

    return {
        "report": serialize_report(report),
        "blockchain": serialize_prediction_anchor(
            anchor
        )
    }


@router.post("/", status_code=201)
def generate_report(
    payload: ReportCreate,
    db: Session = Depends(get_db)
):

    try:

        report, anchor = create_medical_report(
            db,
            payload.prediction_id
        )

        return {
            "report": serialize_report(report),
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
            status_code=409,
            detail=str(exc)
        )

    except Exception:

        db.rollback()

        logger.exception(
            "Medical report generation failed"
        )

        raise HTTPException(
            status_code=503,
            detail="Report generation unavailable"
        )


@router.get("/")
def list_reports(
    patient_id: int | None = None,
    db: Session = Depends(get_db)
):

    statement = select(MedicalReport)

    if patient_id is not None:

        statement = statement.where(
            MedicalReport.patient_id == patient_id
        )

    statement = statement.order_by(
        MedicalReport.id.desc()
    )

    reports = db.scalars(statement).all()

    return [
        report_response(db, report)
        for report in reports
    ]


@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):

    report = get_report_or_404(
        db,
        report_id
    )

    return report_response(
        db,
        report
    )


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db)
):

    report = get_report_or_404(
        db,
        report_id
    )

    file_path = (
        REPORT_DIR / report.file_name
    ).resolve()

    if (
        file_path.parent != REPORT_DIR.resolve()
        or not file_path.is_file()
    ):

        raise HTTPException(
            status_code=404,
            detail="Report file not found"
        )

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=report.file_name
    )


@router.post("/{report_id}/verify")
def verify_uploaded_report(
    report_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    report = get_report_or_404(
        db,
        report_id
    )

    try:

        content = file.file.read(
            MAX_FILE_SIZE + 1
        )

    finally:

        file.file.close()

    if len(content) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 10 MB"
        )

    if not content.startswith(b"%PDF-"):

        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    return verify_medical_report(
        db,
        report,
        content
    )


@router.post("/{report_id}/retry-anchor")
def retry_report_anchor(
    report_id: int,
    db: Session = Depends(get_db)
):

    report = get_report_or_404(
        db,
        report_id
    )

    anchor = find_anchor(
        db,
        "medical_report",
        report.id,
        report.version
    )

    if anchor is None:

        raise HTTPException(
            status_code=404,
            detail="Report anchor not found"
        )

    anchor = submit_anchor(
        db,
        anchor.id
    )

    return serialize_prediction_anchor(
        anchor
    )