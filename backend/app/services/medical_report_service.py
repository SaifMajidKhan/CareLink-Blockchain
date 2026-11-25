from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from sqlalchemy.orm import Session

from backend.app.models.patient import Patient
from backend.app.models.ai_prediction import AIPrediction
from backend.app.models.medical_report import MedicalReport
from backend.app.models.blockchain_anchor import BlockchainAnchor

from backend.app.services.prediction_record_service import (
    verify_prediction
)

from backend.app.services.anchor_service import (
    get_blockchain_configuration,
    find_anchor,
    submit_anchor,
    validate_anchor_network
)

from blockchain.services.hashing_service import (
    generate_record_reference,
    generate_salt,
    SERIALIZATION_VERSION
)

from blockchain.services.report_service import (
    generate_file_fingerprint
)

from blockchain.services.blockchain_service import (
    BlockchainService
)


REPORT_DIR = (
    Path(__file__).resolve().parents[2]
    / "generated_reports"
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def generate_pdf(
    file_path,
    patient,
    prediction,
    record_ref
):

    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    elements = []

    elements.append(
        Paragraph(
            "CareLink",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "AI Medication Adherence Risk Report",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 18))

    rows = [
        ["Patient Information", "Details"],
        ["Patient ID", str(patient.id)],
        [
            "Patient Name",
            Paragraph(
                escape(patient.name),
                styles["Normal"]
            )
        ],
        ["Age", str(prediction.input_features["age"])],
        [
            "Condition",
            Paragraph(
                escape(patient.condition),
                styles["Normal"]
            )
        ],
        ["Prediction ID", str(prediction.id)],
        [
            "Generated At",
            datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M UTC"
            )
        ]
    ]

    patient_table = Table(
        rows,
        colWidths=[155, 340]
    )

    patient_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0), (-1, 0),
                colors.HexColor("#0F766E")
            ),
            (
                "TEXTCOLOR",
                (0, 0), (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0), (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1), (-1, -1),
                [
                    colors.HexColor("#F0FDFA"),
                    colors.white
                ]
            ),
            (
                "BOTTOMPADDING",
                (0, 0), (-1, -1), 10
            ),
            (
                "TOPPADDING",
                (0, 0), (-1, -1), 10
            )
        ])
    )

    elements.append(patient_table)
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "AI Risk Assessment",
            styles["Heading2"]
        )
    )

    risk_score = prediction.risk_score_bps / 100

    risk_colors = {
        "Low": "#15803D",
        "Medium": "#D97706",
        "High": "#DC2626"
    }

    risk_color = risk_colors.get(
        prediction.risk_level,
        "#333333"
    )

    elements.append(
        Paragraph(
            f'<font color="{risk_color}" size="24">'
            f'<b>{risk_score:.2f}%</b></font>',
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            f"Risk classification: "
            f"<b>{escape(prediction.risk_level)}</b>",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 10))

    features = prediction.input_features

    adherence = (
        features["adherence_rate_30d"] * 100
    )

    elements.append(
        Paragraph(
            f"30-day adherence input: "
            f"{adherence:.2f}%",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Missed doses in seven days: "
            f"{features['missed_doses_7d']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Model: {escape(prediction.model_version)}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Algorithm: {escape(prediction.algorithm)}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "Blockchain Integrity",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            "This report has been prepared for "
            "blockchain fingerprint registration. "
            "Use CareLink to check its registration "
            "and integrity status.",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 8))

    elements.append(
        Paragraph(
            f"Report reference: {record_ref}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "<b>Disclaimer:</b> Synthetic-data "
            "academic demonstration only. "
            "The AI model is not clinically validated. "
            "This report is not medical advice.",
            styles["Normal"]
        )
    )

    document.build(elements)


def create_medical_report(
    db: Session,
    prediction_id: int
):

    prediction = db.get(
        AIPrediction,
        prediction_id
    )

    if prediction is None:
        raise LookupError(
            "Prediction not found"
        )

    verification = verify_prediction(
        db,
        prediction
    )

    if verification["verified"] is not True:
        raise ValueError(
            "Prediction must pass integrity verification"
        )

    patient = db.get(
        Patient,
        prediction.patient_id
    )

    if patient is None:
        raise LookupError(
            "Patient not found"
        )

    configuration = get_blockchain_configuration()

    record_ref = generate_record_reference()

    file_name = (
        f"carelink_{record_ref[2:]}.pdf"
    )

    file_path = REPORT_DIR / file_name

    try:

        generate_pdf(
            file_path,
            patient,
            prediction,
            record_ref
        )

        report = MedicalReport(
            patient_id=patient.id,
            prediction_id=prediction.id,
            record_ref=record_ref,
            version=1,
            file_name=file_name
        )

        db.add(report)
        db.flush()

        salt = generate_salt()

        fingerprint = generate_file_fingerprint(
            file_path,
            salt
        )

        anchor = BlockchainAnchor(
            entity_type="medical_report",
            entity_id=report.id,
            record_ref=record_ref,
            version=1,
            serialization_version=SERIALIZATION_VERSION,
            salt=salt,
            fingerprint=fingerprint,
            chain_id=configuration["chain_id"],
            contract_address=configuration["contract_address"],
            status="pending"
        )

        db.add(anchor)

        # Save report and anchor before contacting Ethereum.
        db.commit()

    except Exception:

        db.rollback()

        file_path.unlink(
            missing_ok=True
        )

        raise

    db.refresh(report)
    db.refresh(anchor)

    anchor = submit_anchor(
        db,
        anchor.id
    )

    return report, anchor


def verify_medical_report(
    db: Session,
    report: MedicalReport,
    file_content: bytes
):

    result = {
        "report_id": report.id,
        "record_ref": report.record_ref,
        "version": report.version
    }

    anchor = find_anchor(
        db,
        "medical_report",
        report.id,
        report.version
    )

    if anchor is None:

        return {
            **result,
            "status": "not_registered",
            "verified": None
        }

    if anchor.record_ref != report.record_ref:

        return {
            **result,
            "status": "mismatch",
            "verified": False
        }

    if (
        anchor.serialization_version
        != SERIALIZATION_VERSION
    ):

        return {
            **result,
            "status": "verification_unavailable",
            "verified": None
        }

    temporary_path = None

    try:

        with NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as temporary_file:

            temporary_path = Path(
                temporary_file.name
            )

            temporary_file.write(
                file_content
            )

        fingerprint = generate_file_fingerprint(
            temporary_path,
            anchor.salt
        )

        service = BlockchainService()

        validate_anchor_network(
            service,
            anchor
        )

        verification = service.verify_record(
            record_ref=anchor.record_ref,
            version=anchor.version,
            fingerprint=fingerprint
        )

        return {
            **result,
            **verification
        }

    except Exception:

        return {
            **result,
            "status": "verification_unavailable",
            "verified": None
        }

    finally:

        if temporary_path is not None:

            temporary_path.unlink(
                missing_ok=True
            )


def serialize_report(report):

    return {
        "id": report.id,
        "patient_id": report.patient_id,
        "prediction_id": report.prediction_id,
        "record_ref": report.record_ref,
        "version": report.version,
        "file_name": report.file_name,
        "created_at": report.created_at,
        "download_url": (
            f"/reports/{report.id}/download"
        )
    }