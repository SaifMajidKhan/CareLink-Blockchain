import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from blockchain.services.blockchain_service import (
    BlockchainService
)

from blockchain.services.report_service import (
    ReportIntegrityService
)


BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "demo_reports"

REPORT_DIR.mkdir(exist_ok=True)


def create_report(
    file_path,
    adherence,
    risk_level
):

    pdf = canvas.Canvas(str(file_path), pagesize=A4)

    width, height = A4

    # Header
    pdf.setFillColor(colors.HexColor("#123B52"))
    pdf.rect(0, height - 110, width, 110, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawString(40, height - 55, "CareLink")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        40,
        height - 80,
        "Medication Adherence Report"
    )

    # Patient information
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 15)

    pdf.drawString(
        40,
        height - 155,
        "Patient Information"
    )

    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        40,
        height - 185,
        "Patient Reference: PAT-DEMO-001"
    )

    pdf.drawString(
        40,
        height - 210,
        "Medication: Metformin"
    )

    # Adherence information
    pdf.setFont("Helvetica-Bold", 15)

    pdf.drawString(
        40,
        height - 270,
        "Adherence Summary"
    )

    pdf.setFont("Helvetica-Bold", 36)

    pdf.drawString(
        40,
        height - 330,
        f"{adherence}%"
    )

    pdf.setFillColor(colors.lightgrey)
    pdf.rect(
        40, height - 360,
        500, 15, fill=1, stroke=0
    )

    pdf.setFillColor(colors.HexColor("#168C80"))
    pdf.rect(
        40, height - 360,
        500 * adherence / 100,
        15, fill=1, stroke=0
    )

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 14)

    pdf.drawString(
        40,
        height - 405,
        f"Risk Level: {risk_level}"
    )

    # Footer
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.grey)

    pdf.drawString(
        40,
        50,
        "CareLink - Synthetic demonstration report"
    )

    pdf.save()


original_path = REPORT_DIR / "original_report.pdf"
modified_path = REPORT_DIR / "modified_report.pdf"

# Generate two different reports
create_report(original_path, 65, "High")
create_report(modified_path, 95, "Low")

print("\nPDF reports generated successfully!")

blockchain = BlockchainService()

report_service = ReportIntegrityService(blockchain)


# Register original report

registration = report_service.register_report(
    original_path
)

print("\n========== REPORT REGISTRATION ==========")

# Do not display the secret salt
print(json.dumps({
    key: value
    for key, value in registration.items()
    if key != "salt"
}, indent=4))


# Verify original report

original_result = report_service.verify_report(
    original_path,
    registration["record_ref"],
    registration["salt"]
)

print("\n========== ORIGINAL REPORT ==========")
print(json.dumps(original_result, indent=4))

assert original_result["verified"] is True


# Verify altered report against original anchor

modified_result = report_service.verify_report(
    modified_path,
    registration["record_ref"],
    registration["salt"]
)

print("\n========== MODIFIED REPORT ==========")
print(json.dumps(modified_result, indent=4))

assert modified_result["verified"] is False


print("\nOriginal report:", original_path)
print("Modified report:", modified_path)

print("\nPDF INTEGRITY CHECKS PASSED!")