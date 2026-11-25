// SPDX-License-Identifier: MIT
pragma solidity ^0.8.34;

contract CareLinkIntegrity {

    address public immutable owner;

    mapping(address => bool) public authorizedWriters;

    struct Record {
        bytes32 fingerprint;
        uint256 registeredAt;
        address registeredBy;
        bool exists;
    }

    mapping(bytes32 => mapping(uint256 => Record))
        private records;

    mapping(bytes32 => uint256)
        private latestVersions;

    event WriterAuthorized(address indexed writer);

    event WriterRevoked(address indexed writer);

    event RecordRegistered(
        bytes32 indexed recordRef,
        uint256 indexed version,
        bytes32 fingerprint,
        address indexed registeredBy,
        uint256 registeredAt
    );

    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "Only owner can perform this action"
        );
        _;
    }

    modifier onlyAuthorizedWriter() {
        require(
            authorizedWriters[msg.sender],
            "Unauthorized writer"
        );
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedWriters[msg.sender] = true;

        emit WriterAuthorized(msg.sender);
    }

    function authorizeWriter(address writer)
        external
        onlyOwner
    {
        require(
            writer != address(0),
            "Invalid writer address"
        );

        authorizedWriters[writer] = true;

        emit WriterAuthorized(writer);
    }

    function revokeWriter(address writer)
        external
        onlyOwner
    {
        require(
            writer != owner,
            "Cannot revoke owner"
        );

        authorizedWriters[writer] = false;

        emit WriterRevoked(writer);
    }

    function registerRecord(
        bytes32 recordRef,
        uint256 version,
        bytes32 fingerprint
    )
        external
        onlyAuthorizedWriter
    {
        require(
            recordRef != bytes32(0),
            "Invalid record reference"
        );

        require(
            fingerprint != bytes32(0),
            "Invalid fingerprint"
        );

        require(
            !records[recordRef][version].exists,
            "Record version already exists"
        );

        require(
            version == latestVersions[recordRef] + 1,
            "Invalid record version"
        );

        records[recordRef][version] = Record({
            fingerprint: fingerprint,
            registeredAt: block.timestamp,
            registeredBy: msg.sender,
            exists: true
        });

        latestVersions[recordRef] = version;

        emit RecordRegistered(
            recordRef,
            version,
            fingerprint,
            msg.sender,
            block.timestamp
        );
    }

    function getRecord(
        bytes32 recordRef,
        uint256 version
    )
        external
        view
        returns (Record memory)
    {
        require(
            records[recordRef][version].exists,
            "Record not found"
        );

        return records[recordRef][version];
    }

    function verifyRecord(
        bytes32 recordRef,
        uint256 version,
        bytes32 fingerprint
    )
        external
        view
        returns (bool)
    {
        require(
            records[recordRef][version].exists,
            "Record not found"
        );

        return records[recordRef][version].fingerprint
            == fingerprint;
    }

    function recordExists(
        bytes32 recordRef,
        uint256 version
    )
        external
        view
        returns (bool)
    {
        return records[recordRef][version].exists;
    }

    function getLatestVersion(bytes32 recordRef)
        external
        view
        returns (uint256)
    {
        return latestVersions[recordRef];
    }
}