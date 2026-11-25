import json

from blockchain.services.blockchain_service import (
    BlockchainService
)

from blockchain.services.hashing_service import (
    generate_record_reference,
    generate_salt,
    generate_fingerprint
)


service = BlockchainService()

record_ref = generate_record_reference()
salt = generate_salt()

record = {
    "patient_ref": "PAT-DEMO-001",
    "status": "Taken",
    "version": 1
}

fingerprint = generate_fingerprint(
    record,
    salt
)


# First registration

first_result = service.register_record_safe(
    record_ref,
    1,
    fingerprint
)

print("\n========== FIRST REGISTRATION ==========")
print(json.dumps(first_result, indent=4))

assert first_result["status"] == "registered"

block_before_retry = service.web3.eth.block_number


# Retry the same registration

retry_result = service.register_record_safe(
    record_ref,
    1,
    fingerprint
)

print("\n========== SAFE RETRY ==========")
print(json.dumps(retry_result, indent=4))

assert retry_result["status"] == "already_registered"

assert (
    service.web3.eth.block_number
    == block_before_retry
)


# Attempt conflicting registration

modified = {
    **record,
    "status": "Missed"
}

modified_hash = generate_fingerprint(
    modified,
    salt
)

print("\n========== CONFLICT DETECTION ==========")

try:

    service.register_record_safe(
        record_ref,
        1,
        modified_hash
    )

except ValueError as error:

    print("Conflict correctly rejected:", error)

else:

    raise AssertionError(
        "Conflicting registration was not rejected"
    )


print("\nALL RETRY CHECKS PASSED!")