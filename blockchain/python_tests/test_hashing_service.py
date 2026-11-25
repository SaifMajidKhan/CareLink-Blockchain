import pytest

from blockchain.services.hashing_service import (
    generate_record_reference,
    generate_salt,
    generate_fingerprint
)


@pytest.fixture
def record():

    return {
        "patient_ref": "PAT-DEMO-001",
        "medication": "Metformin",
        "status": "Taken",
        "version": 1
    }


def test_deterministic_fingerprint(record):

    salt = generate_salt()

    assert (
        generate_fingerprint(record, salt)
        == generate_fingerprint(record, salt)
    )


def test_modified_record_changes_fingerprint(record):

    salt = generate_salt()

    modified = {
        **record,
        "status": "Missed"
    }

    assert (
        generate_fingerprint(record, salt)
        != generate_fingerprint(modified, salt)
    )


def test_different_salts_change_fingerprint(record):

    assert (
        generate_fingerprint(record, generate_salt())
        != generate_fingerprint(record, generate_salt())
    )


def test_dictionary_order_does_not_change_hash(record):

    salt = generate_salt()

    reordered = dict(
        reversed(list(record.items()))
    )

    assert (
        generate_fingerprint(record, salt)
        == generate_fingerprint(reordered, salt)
    )


def test_version_change_changes_fingerprint(record):

    salt = generate_salt()

    modified = {
        **record,
        "version": 2
    }

    assert (
        generate_fingerprint(record, salt)
        != generate_fingerprint(modified, salt)
    )


def test_invalid_salt_rejected(record):

    with pytest.raises(ValueError):

        generate_fingerprint(record, "abcd")


def test_fingerprint_length(record):

    fingerprint = generate_fingerprint(
        record,
        generate_salt()
    )

    assert fingerprint.startswith("0x")
    assert len(fingerprint) == 66


def test_unique_record_references():

    references = {
        generate_record_reference()
        for _ in range(100)
    }

    assert len(references) == 100

    for reference in references:

        assert reference.startswith("0x")
        assert len(reference) == 66


def test_salt_length():

    salt = generate_salt()

    assert len(bytes.fromhex(salt)) == 32


def test_nan_values_rejected():

    with pytest.raises(ValueError):

        generate_fingerprint(
            {"risk_score": float("nan")},
            generate_salt()
        )