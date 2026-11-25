from datetime import timezone

from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.schemas.medication import MedicationCorrection

from backend.app.models.patient import Patient
from backend.app.models.medication_event import (
    MedicationEvent
)
from backend.app.models.blockchain_anchor import (
    BlockchainAnchor
)

from backend.app.schemas.medication import (
    MedicationCreate
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
    generate_fingerprint,
    SERIALIZATION_VERSION
)

from blockchain.services.blockchain_service import (
    BlockchainService
)


def build_medication_payload(
    medication: MedicationEvent
):

    return {
        "record_type": "medication_event",
        "record_ref": medication.record_ref,
        "version": medication.version,
        "patient_id": medication.patient_id,
        "medication_name": medication.medication_name,
        "dosage": medication.dosage,
        "status": medication.status,
        "scheduled_at": medication.scheduled_at
        .astimezone(timezone.utc)
        .isoformat(timespec="microseconds")
    }


def create_medication(
    db: Session,
    payload: MedicationCreate
):

    patient = db.get(
        Patient,
        payload.patient_id
    )

    if patient is None:
        raise LookupError("Patient not found")

    configuration = get_blockchain_configuration()

    record_ref = generate_record_reference()

    medication = MedicationEvent(
        patient_id=payload.patient_id,
        record_ref=record_ref,
        version=1,
        medication_name=payload.medication_name,
        dosage=payload.dosage,
        status=payload.status,
        scheduled_at=payload.scheduled_at
        .astimezone(timezone.utc)
    )

    db.add(medication)
    db.flush()

    salt = generate_salt()

    fingerprint = generate_fingerprint(
        build_medication_payload(medication),
        salt
    )

    anchor = BlockchainAnchor(
        entity_type="medication_event",
        entity_id=medication.id,
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

    # Persist both records before contacting Ethereum.
    db.commit()

    db.refresh(medication)
    db.refresh(anchor)

    anchor = submit_anchor(
        db,
        anchor.id
    )

    return medication, anchor


def verify_medication(
    db: Session,
    medication: MedicationEvent
):

    anchor = find_anchor(
        db,
        "medication_event",
        medication.id,
        medication.version
    )

    result = {
        "medication_id": medication.id,
        "record_ref": medication.record_ref,
        "version": medication.version
    }

    if anchor is None:

        return {
            **result,
            "status": "not_registered",
            "verified": None,
            "message": "No blockchain anchor exists"
        }

    if (
        anchor.record_ref != medication.record_ref
        or anchor.version != medication.version
    ):

        return {
            **result,
            "status": "mismatch",
            "verified": False,
            "message": "Record identity does not match anchor"
        }

    if anchor.serialization_version != SERIALIZATION_VERSION:

        return {
            **result,
            "status": "verification_unavailable",
            "verified": None,
            "message": "Unsupported serialization version"
        }

    try:

        current_fingerprint = generate_fingerprint(
            build_medication_payload(medication),
            anchor.salt
        )

        service = BlockchainService()

        validate_anchor_network(service, anchor)

        verification = service.verify_record(
            record_ref=anchor.record_ref,
            version=anchor.version,
            fingerprint=current_fingerprint
        )

        verification_status = verification["status"]

        messages = {
            "verified": (
                "Medication record matches its "
                "blockchain fingerprint"
            ),
            "mismatch": (
                "Medication record does not match "
                "its blockchain fingerprint"
            ),
            "not_registered": (
                "No matching record exists on blockchain"
            ),
            "verification_unavailable": (
                "Blockchain verification is unavailable"
            )
        }

        return {
            **result,
            "status": verification_status,
            "verified": verification["verified"],
            "message": messages.get(
                verification_status,
                "Unknown verification result"
            )
        }

    except Exception:

        return {
            **result,
            "status": "verification_unavailable",
            "verified": None,
            "message": "Unable to verify medication record"
        }

def correct_medication(
    db: Session,
    medication_id: int,
    payload: MedicationCorrection
):

    original = db.get(
        MedicationEvent,
        medication_id
    )

    if original is None:
        raise LookupError(
            "Medication record not found"
        )

    # Lock the first version to serialize corrections
    # belonging to the same logical record.
    first_version = db.scalars(
        select(MedicationEvent)
        .where(
            MedicationEvent.record_ref == original.record_ref,
            MedicationEvent.version == 1
        )
        .with_for_update()
    ).one()

    latest = db.scalars(
        select(MedicationEvent)
        .where(
            MedicationEvent.record_ref == first_version.record_ref
        )
        .order_by(MedicationEvent.version.desc())
        .limit(1)
    ).one()

    if original.id != latest.id:
        raise ValueError(
            "Only the latest version can be corrected"
        )

    previous_anchor = find_anchor(
        db,
        "medication_event",
        latest.id,
        latest.version
    )

    if (
        previous_anchor is None
        or previous_anchor.status != "registered"
    ):
        raise ValueError(
            "Previous version must be registered first"
        )

    verification = verify_medication(
        db,
        latest
    )

    if verification["verified"] is not True:
        raise ValueError(
            "Previous version must pass integrity verification"
        )

    configuration = get_blockchain_configuration()

    if (
        configuration["chain_id"] != previous_anchor.chain_id
        or configuration["contract_address"].lower()
        != previous_anchor.contract_address.lower()
    ):
        raise ValueError(
            "Correction must use the original blockchain contract"
        )

    corrected = MedicationEvent(
        patient_id=latest.patient_id,
        record_ref=latest.record_ref,
        version=latest.version + 1,
        medication_name=payload.medication_name,
        dosage=payload.dosage,
        status=payload.status,
        scheduled_at=payload.scheduled_at.astimezone(
            timezone.utc
        )
    )

    if all(
        getattr(corrected, field) == getattr(latest, field)
        for field in (
            "medication_name",
            "dosage",
            "status",
            "scheduled_at"
        )
    ):
        raise ValueError(
            "Correction contains no changes"
        )

    db.add(corrected)
    db.flush()

    salt = generate_salt()

    fingerprint = generate_fingerprint(
        build_medication_payload(corrected),
        salt
    )

    anchor = BlockchainAnchor(
        entity_type="medication_event",
        entity_id=corrected.id,
        record_ref=corrected.record_ref,
        version=corrected.version,
        serialization_version=SERIALIZATION_VERSION,
        salt=salt,
        fingerprint=fingerprint,
        chain_id=configuration["chain_id"],
        contract_address=configuration["contract_address"],
        status="pending"
    )

    db.add(anchor)
    db.commit()

    db.refresh(corrected)
    db.refresh(anchor)

    anchor = submit_anchor(
        db,
        anchor.id
    )

    return corrected, anchor