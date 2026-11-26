from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fastapi import HTTPException

from backend.app.routers import blockchain


@pytest.fixture
def anchor():

    return SimpleNamespace(
        id=1,
        record_ref="0x" + "11" * 32,
        version=1,
        fingerprint="0x" + "22" * 32,
        chain_id=31337,
        contract_address="0x" + "33" * 20
    )


@pytest.fixture
def db(anchor):

    database = Mock()
    database.get.return_value = anchor

    return database


@pytest.fixture
def service(monkeypatch):

    mock_service = Mock()

    monkeypatch.setattr(
        blockchain,
        "BlockchainService",
        lambda: mock_service
    )

    monkeypatch.setattr(
        blockchain,
        "validate_anchor_network",
        lambda service, anchor: None
    )

    return mock_service


def test_get_existing_anchor(db, anchor):

    result = blockchain.get_anchor(1, db)

    assert result == anchor


def test_missing_anchor_returns_404(db):

    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:

        blockchain.get_anchor(999, db)

    assert exc.value.status_code == 404


@pytest.mark.parametrize(
    "status,verified",
    [
        ("verified", True),
        ("mismatch", False),
        ("not_registered", None),
        ("verification_unavailable", None)
    ]
)
def test_anchor_verification_status(
    db,
    service,
    anchor,
    status,
    verified
):

    service.verify_record.return_value = {
        "status": status,
        "verified": verified
    }

    result = blockchain.verify_anchor(anchor.id, db)

    assert result["anchor_id"] == anchor.id
    assert result["status"] == status
    assert result["verified"] is verified

    service.verify_record.assert_called_once_with(
        record_ref=anchor.record_ref,
        version=anchor.version,
        fingerprint=anchor.fingerprint
    )


def test_blockchain_connection_failure(db, monkeypatch):

    def unavailable():

        raise ConnectionError("Network unavailable")

    monkeypatch.setattr(
        blockchain,
        "BlockchainService",
        unavailable
    )

    result = blockchain.verify_anchor(1, db)

    assert result["status"] == "verification_unavailable"
    assert result["verified"] is None


def test_incorrect_network(db, service, monkeypatch):

    def reject_network(service, anchor):

        raise RuntimeError("Incorrect blockchain")

    monkeypatch.setattr(
        blockchain,
        "validate_anchor_network",
        reject_network
    )

    result = blockchain.verify_anchor(1, db)

    assert result["status"] == "verification_unavailable"
    assert result["verified"] is None

    service.verify_record.assert_not_called()


def test_registration_summary(db):

    db.execute.return_value.all.return_value = [
        ("medication_event", "registered", 5),
        ("ai_prediction", "registered", 2),
        ("medical_report", "registered", 4),
        ("medical_report", "pending", 1),
        ("medication_event", "failed", 1)
    ]

    result = blockchain.blockchain_summary(db)

    assert result["total"] == 13
    assert result["registered"] == 11
    assert result["pending"] == 1
    assert result["failed"] == 1
    assert result["medication_events"] == 6
    assert result["ai_predictions"] == 2
    assert result["medical_reports"] == 5


def test_empty_registration_summary(db):

    db.execute.return_value.all.return_value = []

    result = blockchain.blockchain_summary(db)

    assert all(value == 0 for value in result.values())


def test_anchor_schema_excludes_sensitive_fields():

    fields = blockchain.BlockchainAnchorResponse.model_fields

    assert "salt" not in fields
    assert "last_error" not in fields
    assert "private_key" not in fields
    assert "fingerprint" in fields
    assert "transaction_hash" in fields