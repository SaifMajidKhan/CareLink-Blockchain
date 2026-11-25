from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

import pytest

from pydantic import ValidationError

from backend.app.schemas.medication import (
    MedicationCreate
)

from backend.app.services.medication_service import (
    build_medication_payload
)

from blockchain.services.hashing_service import (
    generate_fingerprint,
    generate_salt
)


def sample_medication():

    return SimpleNamespace(
        record_ref="0x" + "1" * 64,
        version=1,
        patient_id=1,
        medication_name="Metformin",
        dosage="500 mg",
        status="Taken",
        scheduled_at=datetime(
            2026, 11, 25, 15, 0,
            tzinfo=timezone.utc
        )
    )


def test_valid_medication():

    medication = MedicationCreate(
        patient_id=1,
        medication_name="Metformin",
        dosage="500 mg",
        status="Taken",
        scheduled_at="2026-11-25T20:00:00+05:00"
    )

    assert medication.status == "Taken"


def test_invalid_medication_status():

    with pytest.raises(ValidationError):

        MedicationCreate(
            patient_id=1,
            medication_name="Metformin",
            dosage="500 mg",
            status="Unknown",
            scheduled_at="2026-11-25T20:00:00+05:00"
        )


def test_invalid_patient_id():

    with pytest.raises(ValidationError):

        MedicationCreate(
            patient_id=0,
            medication_name="Metformin",
            dosage="500 mg",
            status="Taken",
            scheduled_at="2026-11-25T20:00:00+05:00"
        )


def test_timezone_required():

    with pytest.raises(ValidationError):

        MedicationCreate(
            patient_id=1,
            medication_name="Metformin",
            dosage="500 mg",
            status="Taken",
            scheduled_at="2026-11-25T20:00:00"
        )


def test_timezone_normalization():

    medication = sample_medication()

    original = build_medication_payload(
        medication
    )

    medication.scheduled_at = (
        medication.scheduled_at.astimezone(
            timezone(timedelta(hours=5))
        )
    )

    converted = build_medication_payload(
        medication
    )

    assert original == converted


def test_medication_status_tampering():

    medication = sample_medication()

    salt = generate_salt()

    original = generate_fingerprint(
        build_medication_payload(medication),
        salt
    )

    medication.status = "Missed"

    modified = generate_fingerprint(
        build_medication_payload(medication),
        salt
    )

    assert original != modified


def test_medication_dosage_tampering():

    medication = sample_medication()

    salt = generate_salt()

    original = generate_fingerprint(
        build_medication_payload(medication),
        salt
    )

    medication.dosage = "1000 mg"

    modified = generate_fingerprint(
        build_medication_payload(medication),
        salt
    )

    assert original != modified


def test_medication_version_changes_fingerprint():

    medication = sample_medication()

    salt = generate_salt()

    original = generate_fingerprint(
        build_medication_payload(medication),
        salt
    )

    medication.version = 2

    modified = generate_fingerprint(
        build_medication_payload(medication),
        salt
    )

    assert original != modified