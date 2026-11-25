from datetime import timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models.patient import Patient

from backend.app.models.ai_prediction import AIPrediction

from backend.app.models.blockchain_anchor import BlockchainAnchor

from backend.app.schemas.prediction import PredictionCreate

from backend.app.services.prediction_service import (
    predict_adherence_risk
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


def build_prediction_payload(prediction: AIPrediction):

    return {
        "record_type": "ai_prediction",
        "record_ref": prediction.record_ref,
        "version": prediction.version,
        "patient_id": prediction.patient_id,
        "input_features": prediction.input_features,
        "risk_score_bps": prediction.risk_score_bps,
        "risk_level": prediction.risk_level,
        "model_version": prediction.model_version,
        "model_sha256": prediction.model_sha256,
        "algorithm": prediction.algorithm,
        "dataset_type": prediction.dataset_type,
        "created_at": prediction.created_at
        .astimezone(timezone.utc)
        .isoformat(timespec="microseconds")
    }


def create_prediction(
    db: Session,
    payload: PredictionCreate
):

    patient = db.get(
        Patient,
        payload.patient_id
    )

    if patient is None:
        raise LookupError("Patient not found")

    if patient.age != payload.features.age:
        raise ValueError(
            "Prediction age must match patient age"
        )

    configuration = get_blockchain_configuration()

    result = predict_adherence_risk(
        payload.features
    )

    record_ref = generate_record_reference()

    risk_score_bps = int(
        Decimal(str(result["risk_score"])) * 100
    )

    prediction = AIPrediction(
        patient_id=payload.patient_id,
        record_ref=record_ref,
        version=1,
        input_features=payload.features.model_dump(
            mode="json"
        ),
        risk_score_bps=risk_score_bps,
        risk_level=result["risk_level"],
        model_version=result["model_version"],
        model_sha256=result["model_sha256"],
        algorithm=result["algorithm"],
        dataset_type=result["dataset_type"]
    )

    db.add(prediction)
    db.flush()
    db.refresh(prediction)

    salt = generate_salt()

    fingerprint = generate_fingerprint(
        build_prediction_payload(prediction),
        salt
    )

    anchor = BlockchainAnchor(
        entity_type="ai_prediction",
        entity_id=prediction.id,
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

    # Persist prediction and anchor before
    # contacting the blockchain.
    db.commit()

    db.refresh(prediction)
    db.refresh(anchor)

    anchor = submit_anchor(
        db,
        anchor.id
    )

    return prediction, anchor


def verify_prediction(
    db: Session,
    prediction: AIPrediction
):

    anchor = find_anchor(
        db,
        "ai_prediction",
        prediction.id,
        prediction.version
    )

    result = {
        "prediction_id": prediction.id,
        "record_ref": prediction.record_ref,
        "version": prediction.version
    }

    if anchor is None:

        return {
            **result,
            "status": "not_registered",
            "verified": None
        }

    if (
        anchor.record_ref != prediction.record_ref
        or anchor.version != prediction.version
    ):

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

    try:

        fingerprint = generate_fingerprint(
            build_prediction_payload(prediction),
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


def serialize_prediction(
    prediction: AIPrediction
):

    return {
        "id": prediction.id,
        "patient_id": prediction.patient_id,
        "record_ref": prediction.record_ref,
        "version": prediction.version,
        "input_features": prediction.input_features,
        "risk_score": prediction.risk_score_bps / 100,
        "risk_level": prediction.risk_level,
        "model_version": prediction.model_version,
        "model_sha256": prediction.model_sha256,
        "algorithm": prediction.algorithm,
        "dataset_type": prediction.dataset_type,
        "created_at": prediction.created_at,
        "disclaimer": (
            "Synthetic-data demonstration only. "
            "Not clinically validated."
        )
    }


def serialize_prediction_anchor(anchor):

    if anchor is None:
        return None

    return {
        "record_ref": anchor.record_ref,
        "version": anchor.version,
        "fingerprint": anchor.fingerprint,
        "transaction_hash": anchor.transaction_hash,
        "block_number": anchor.block_number,
        "chain_id": anchor.chain_id,
        "contract_address": anchor.contract_address,
        "status": anchor.status,
        "retry_count": anchor.retry_count,
        "anchored_at": anchor.anchored_at
    }