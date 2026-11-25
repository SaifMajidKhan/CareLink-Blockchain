import json

from blockchain.services.hashing_service import (
    generate_record_reference,
    generate_salt,
    generate_fingerprint
)

from blockchain.services.blockchain_service import (
    BlockchainService
)


def display(title, result):

    print(f"\n========== {title} ==========")

    print(json.dumps(result, indent=4))


service = BlockchainService()

print("Blockchain connected successfully!")
print("Writer authorized:", service.is_writer_authorized())


# 1. Original medication record

record_ref = generate_record_reference()
salt = generate_salt()

medication_record = {
    "patient_ref": "PAT-DEMO-001",
    "medication": "Metformin",
    "status": "Taken",
    "scheduled_time": "20:00",
    "version": 1
}

original_hash = generate_fingerprint(
    medication_record,
    salt
)

registration = service.register_record(
    record_ref,
    1,
    original_hash
)

display("MEDICATION REGISTRATION", registration)


# 2. Verify original record

verification = service.verify_record(
    record_ref,
    1,
    generate_fingerprint(medication_record, salt)
)

display("ORIGINAL VERIFICATION", verification)

assert verification["verified"] is True


# 3. Detect tampering

tampered_record = {
    **medication_record,
    "status": "Missed"
}

tampered_hash = generate_fingerprint(
    tampered_record,
    salt
)

tampered_result = service.verify_record(
    record_ref,
    1,
    tampered_hash
)

display("TAMPERING DETECTION", tampered_result)

assert tampered_result["verified"] is False


# 4. Register legitimate correction

corrected_record = {
    **medication_record,
    "status": "Missed",
    "version": 2
}

correction_salt = generate_salt()

corrected_hash = generate_fingerprint(
    corrected_record,
    correction_salt
)

correction = service.register_record(
    record_ref,
    2,
    corrected_hash
)

display("CORRECTION REGISTRATION", correction)


# 5. Retrieve version history

display(
    "VERSION 1",
    service.get_record(record_ref, 1)
)

display(
    "VERSION 2",
    service.get_record(record_ref, 2)
)

assert service.get_latest_version(record_ref) == 2

assert service.verify_record(
    record_ref, 1, original_hash
)["verified"] is True

assert service.verify_record(
    record_ref, 2, corrected_hash
)["verified"] is True


# 6. Register a simulated AI prediction

prediction_ref = generate_record_reference()
prediction_salt = generate_salt()

prediction = {
    "patient_ref": "PAT-DEMO-001",
    "risk_level": "High",
    "risk_score": 85,
    "model_version": "demo-v1",
    "version": 1
}

prediction_hash = generate_fingerprint(
    prediction,
    prediction_salt
)

ai_registration = service.register_record(
    prediction_ref,
    1,
    prediction_hash
)

display("AI PREDICTION REGISTRATION", ai_registration)

ai_verification = service.verify_record(
    prediction_ref,
    1,
    prediction_hash
)

display("AI PREDICTION VERIFICATION", ai_verification)

assert ai_verification["verified"] is True


# 7. Detect modified AI prediction

modified_prediction = {
    **prediction,
    "risk_level": "Low",
    "risk_score": 15
}

modified_hash = generate_fingerprint(
    modified_prediction,
    prediction_salt
)

modified_result = service.verify_record(
    prediction_ref,
    1,
    modified_hash
)

display("AI PREDICTION TAMPERING", modified_result)

assert modified_result["verified"] is False


# 8. Verify an unregistered record

missing_result = service.verify_record(
    generate_record_reference(),
    1,
    original_hash
)

display("UNREGISTERED RECORD", missing_result)

assert missing_result["status"] == "not_registered"


print("\n====================================")
print("ALL INTEGRATION CHECKS PASSED!")
print("====================================")