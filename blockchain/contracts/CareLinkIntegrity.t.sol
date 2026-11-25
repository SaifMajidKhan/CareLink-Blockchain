// SPDX-License-Identifier: MIT
pragma solidity ^0.8.34;

import {Test} from "forge-std/Test.sol";
import {CareLinkIntegrity} from "./CareLinkIntegrity.sol";

contract CareLinkIntegrityTest is Test {

    CareLinkIntegrity private registry;

    address private writer = address(0x123);
    address private outsider = address(0x456);

    bytes32 private recordRef =
        keccak256("MED-DEMO-001");

    bytes32 private originalHash =
        sha256("Medication status: Taken");

    bytes32 private tamperedHash =
        sha256("Medication status: Missed");

    function setUp() public {
        registry = new CareLinkIntegrity();
    }

    // 1. Verify contract ownership
    function test_OwnerInitialized() public view {
        assertEq(registry.owner(), address(this));
    }

    // 2. Owner should be an authorized writer
    function test_OwnerIsAuthorized() public view {
        assertTrue(
            registry.authorizedWriters(address(this))
        );
    }

    // 3. Register a medication record
    function test_RegisterRecord() public {
        registry.registerRecord(
            recordRef,
            1,
            originalHash
        );

        assertTrue(
            registry.recordExists(recordRef, 1)
        );

        CareLinkIntegrity.Record memory record =
            registry.getRecord(recordRef, 1);

        assertEq(record.fingerprint, originalHash);
        assertEq(record.registeredBy, address(this));
        assertEq(record.registeredAt, block.timestamp);
    }

    // 4. Verify an original fingerprint
    function test_VerifyOriginalRecord() public {
        registry.registerRecord(
            recordRef, 1, originalHash
        );

        assertTrue(
            registry.verifyRecord(
                recordRef, 1, originalHash
            )
        );
    }

    // 5. Detect a tampered fingerprint
    function test_DetectTampering() public {
        registry.registerRecord(
            recordRef, 1, originalHash
        );

        assertFalse(
            registry.verifyRecord(
                recordRef, 1, tamperedHash
            )
        );
    }

    // 6. Prevent duplicate registrations
    function test_RejectDuplicateVersion() public {
        registry.registerRecord(
            recordRef, 1, originalHash
        );

        vm.expectRevert(
            bytes("Record version already exists")
        );

        registry.registerRecord(
            recordRef, 1, tamperedHash
        );
    }

    // 7. Prevent unauthorized registration
    function test_RejectUnauthorizedWriter() public {
        vm.prank(outsider);

        vm.expectRevert(
            bytes("Unauthorized writer")
        );

        registry.registerRecord(
            recordRef, 1, originalHash
        );
    }

    // 8. Authorize a new writer
    function test_AuthorizeWriter() public {
        registry.authorizeWriter(writer);

        assertTrue(
            registry.authorizedWriters(writer)
        );

        vm.prank(writer);

        registry.registerRecord(
            recordRef, 1, originalHash
        );

        assertTrue(
            registry.recordExists(recordRef, 1)
        );
    }

    // 9. Revoke writer permissions
    function test_RevokeWriter() public {
        registry.authorizeWriter(writer);
        registry.revokeWriter(writer);

        assertFalse(
            registry.authorizedWriters(writer)
        );

        vm.prank(writer);

        vm.expectRevert(
            bytes("Unauthorized writer")
        );

        registry.registerRecord(
            recordRef, 1, originalHash
        );
    }

    // 10. Register a legitimate correction
    function test_RegisterNewVersion() public {
        registry.registerRecord(
            recordRef, 1, originalHash
        );

        registry.registerRecord(
            recordRef, 2, tamperedHash
        );

        assertEq(
            registry.getLatestVersion(recordRef),
            2
        );
    }

    // 11. Preserve the original version
    function test_PreserveOriginalVersion() public {
        registry.registerRecord(
            recordRef, 1, originalHash
        );

        registry.registerRecord(
            recordRef, 2, tamperedHash
        );

        assertTrue(
            registry.verifyRecord(
                recordRef, 1, originalHash
            )
        );

        assertTrue(
            registry.verifyRecord(
                recordRef, 2, tamperedHash
            )
        );
    }

    // 12. Prevent skipped versions
    function test_RejectSkippedVersion() public {
        registry.registerRecord(
            recordRef, 1, originalHash
        );

        vm.expectRevert(
            bytes("Invalid record version")
        );

        registry.registerRecord(
            recordRef, 3, tamperedHash
        );
    }

    // 13. Reject nonexistent records
    function test_RejectNonexistentRecord() public {
        vm.expectRevert(
            bytes("Record not found")
        );

        registry.verifyRecord(
            recordRef, 1, originalHash
        );
    }

    // 14. Reject empty fingerprints
    function test_RejectEmptyFingerprint() public {
        vm.expectRevert(
            bytes("Invalid fingerprint")
        );

        registry.registerRecord(
            recordRef, 1, bytes32(0)
        );
    }

    // 15. Reject empty record references
    function test_RejectEmptyReference() public {
        vm.expectRevert(
            bytes("Invalid record reference")
        );

        registry.registerRecord(
            bytes32(0), 1, originalHash
        );
    }

    // 16. Register an AI prediction fingerprint
    function test_RegisterAIPrediction() public {
        bytes32 predictionRef =
            keccak256("AI-DEMO-001");

        bytes32 predictionHash =
            sha256("Adherence risk: High");

        registry.registerRecord(
            predictionRef,
            1,
            predictionHash
        );

        assertTrue(
            registry.verifyRecord(
                predictionRef,
                1,
                predictionHash
            )
        );
    }

    // 17. Prevent unauthorized administration
    function test_RejectUnauthorizedAdmin() public {
        vm.prank(outsider);

        vm.expectRevert(
            bytes("Only owner can perform this action")
        );

        registry.authorizeWriter(writer);
    }

    // 18. Prevent revocation of the owner
    function test_CannotRevokeOwner() public {
        vm.expectRevert(
            bytes("Cannot revoke owner")
        );

        registry.revokeWriter(address(this));
    }
}