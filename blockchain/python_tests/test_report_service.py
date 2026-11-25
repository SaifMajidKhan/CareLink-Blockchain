import pytest

from reportlab.pdfgen import canvas

from blockchain.services.hashing_service import (
    generate_salt,
    generate_fingerprint
)

from blockchain.services.report_service import (
    generate_file_fingerprint
)


@pytest.fixture
def sample_report(tmp_path):

    path = tmp_path / "report.pdf"

    pdf = canvas.Canvas(str(path))

    pdf.drawString(
        100, 750,
        "Medication Adherence: 65%"
    )

    pdf.save()

    return path


def test_same_pdf_same_fingerprint(sample_report):

    salt = generate_salt()

    assert (
        generate_file_fingerprint(sample_report, salt)
        == generate_file_fingerprint(sample_report, salt)
    )


def test_modified_pdf_changes_fingerprint(
    sample_report,
    tmp_path
):

    salt = generate_salt()

    modified = tmp_path / "modified.pdf"

    modified.write_bytes(
        sample_report.read_bytes() + b"\n% modified"
    )

    assert (
        generate_file_fingerprint(sample_report, salt)
        != generate_file_fingerprint(modified, salt)
    )


def test_pdf_different_salts(sample_report):

    assert (
        generate_file_fingerprint(
            sample_report,
            generate_salt()
        )
        != generate_file_fingerprint(
            sample_report,
            generate_salt()
        )
    )


def test_missing_pdf_rejected(tmp_path):

    with pytest.raises(FileNotFoundError):

        generate_file_fingerprint(
            tmp_path / "missing.pdf",
            generate_salt()
        )


def test_invalid_pdf_salt(sample_report):

    with pytest.raises(ValueError):

        generate_file_fingerprint(
            sample_report,
            "abcd"
        )


def test_file_fingerprint_length(sample_report):

    fingerprint = generate_file_fingerprint(
        sample_report,
        generate_salt()
    )

    assert fingerprint.startswith("0x")
    assert len(fingerprint) == 66


def test_record_and_pdf_hash_domains_differ(
    sample_report
):

    salt = generate_salt()

    record_hash = generate_fingerprint(
        {"adherence": 65},
        salt
    )

    file_hash = generate_file_fingerprint(
        sample_report,
        salt
    )

    assert record_hash != file_hash