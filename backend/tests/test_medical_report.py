from types import SimpleNamespace

import pytest

from pydantic import ValidationError

from backend.app.schemas.report import ReportCreate

from backend.app.services.medical_report_service import (
    generate_pdf
)

from blockchain.services.report_service import (
    generate_file_fingerprint
)

from blockchain.services.hashing_service import (
    generate_salt
)


@pytest.fixture
def report_pdf(tmp_path):

    patient = SimpleNamespace(
        id=1,
        name="Demo Patient",
        condition="Type 2 Diabetes"
    )

    prediction = SimpleNamespace(
        id=1,
        risk_score_bps=9859,
        risk_level="High",
        model_version="carelink-logreg-v1",
        algorithm="Logistic Regression",
        input_features={
            "age": 45,
            "adherence_rate_30d": 0.40,
            "missed_doses_7d": 18
        }
    )

    file_path = tmp_path / "report.pdf"

    generate_pdf(
        file_path,
        patient,
        prediction,
        "0x" + "a" * 64
    )

    return file_path


def test_valid_report_request():

    request = ReportCreate(
        prediction_id=1
    )

    assert request.prediction_id == 1


def test_invalid_prediction_id():

    with pytest.raises(ValidationError):

        ReportCreate(
            prediction_id=0
        )


def test_extra_report_fields_rejected():

    with pytest.raises(ValidationError):

        ReportCreate(
            prediction_id=1,
            risk_score=15
        )


def test_pdf_generation(report_pdf):

    assert report_pdf.exists()

    assert report_pdf.stat().st_size > 0


def test_pdf_signature(report_pdf):

    assert report_pdf.read_bytes().startswith(
        b"%PDF-"
    )


def test_generated_report_hash_determinism(
    report_pdf
):

    salt = generate_salt()

    first = generate_file_fingerprint(
        report_pdf,
        salt
    )

    second = generate_file_fingerprint(
        report_pdf,
        salt
    )

    assert first == second


def test_generated_report_tampering(
    report_pdf,
    tmp_path
):

    salt = generate_salt()

    modified = tmp_path / "modified.pdf"

    modified.write_bytes(
        report_pdf.read_bytes()
        + b"\n% Modified report\n"
    )

    original_hash = generate_file_fingerprint(
        report_pdf,
        salt
    )

    modified_hash = generate_file_fingerprint(
        modified,
        salt
    )

    assert original_hash != modified_hash


def test_identical_report_copy(
    report_pdf,
    tmp_path
):

    salt = generate_salt()

    copied = tmp_path / "copy.pdf"

    copied.write_bytes(
        report_pdf.read_bytes()
    )

    assert generate_file_fingerprint(
        report_pdf,
        salt
    ) == generate_file_fingerprint(
        copied,
        salt
    )