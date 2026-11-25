import { network } from "hardhat";
import { readFileSync } from "node:fs";
import { createHash, randomBytes } from "node:crypto";
import type { Address, Hex } from "viem";

const { viem } = await network.connect();

const publicClient = await viem.getPublicClient();
const [walletClient] = await viem.getWalletClients();

// Read the deployed contract address
const deployments = JSON.parse(
  readFileSync(
    "ignition/deployments/chain-31337/deployed_addresses.json",
    "utf8"
  )
);

const contractAddress =
  deployments[
    "CareLinkIntegrityModule#CareLinkIntegrity"
  ] as Address;

if (!contractAddress) {
  throw new Error("Contract address not found");
}

const bytecode = await publicClient.getCode({
  address: contractAddress,
});

if (!bytecode || bytecode === "0x") {
  throw new Error(
    "Contract not deployed on the current network"
  );
}

const registry = await viem.getContractAt(
  "CareLinkIntegrity",
  contractAddress
);

// Generate SHA-256 fingerprints
function generateHash(data: object): Hex {
  const serialized = JSON.stringify(data);

  return (
    "0x" +
    createHash("sha256")
      .update(serialized, "utf8")
      .digest("hex")
  ) as Hex;
}

// Generate a unique opaque record reference
const recordRef = (
  "0x" + randomBytes(32).toString("hex")
) as Hex;

// Synthetic medication record
const originalRecord = {
  patient_ref: "PAT-DEMO-001",
  medication: "Metformin",
  status: "Taken",
  scheduled_time: "20:00",
  version: 1,
};

const originalHash = generateHash(originalRecord);

console.log("\n========== CARELINK BLOCKCHAIN ==========");

console.log("Contract address:", contractAddress);
console.log("Wallet address:", walletClient.account.address);
console.log("Record reference:", recordRef);
console.log("Original fingerprint:", originalHash);

// 1. Register the original medication record
console.log("\n========== REGISTER RECORD ==========");

const txHash = await registry.write.registerRecord([
  recordRef,
  1n,
  originalHash,
]);

const receipt =
  await publicClient.waitForTransactionReceipt({
    hash: txHash,
  });

if (receipt.status !== "success") {
  throw new Error("Registration transaction failed");
}

console.log("Transaction hash:", txHash);
console.log("Block number:", receipt.blockNumber.toString());
console.log("Gas used:", receipt.gasUsed.toString());
console.log("Transaction status:", receipt.status);

// 2. Retrieve the on-chain record
console.log("\n========== RETRIEVE RECORD ==========");

const storedRecord = await registry.read.getRecord([
  recordRef,
  1n,
]);

console.log("Stored record:", storedRecord);

// 3. Verify the original fingerprint
console.log("\n========== VERIFY ORIGINAL ==========");

const originalVerified =
  await registry.read.verifyRecord([
    recordRef,
    1n,
    originalHash,
  ]);

console.log("Original record verified:", originalVerified);

// 4. Simulate unauthorized data modification
console.log("\n========== TAMPERING DETECTION ==========");

const tamperedRecord = {
  ...originalRecord,
  status: "Missed",
};

const tamperedHash = generateHash(tamperedRecord);

const tamperedVerified =
  await registry.read.verifyRecord([
    recordRef,
    1n,
    tamperedHash,
  ]);

console.log("Modified fingerprint:", tamperedHash);
console.log("Tampered record verified:", tamperedVerified);

// 5. Register a legitimate correction
console.log("\n========== REGISTER CORRECTION ==========");

const correctedRecord = {
  ...originalRecord,
  status: "Missed",
  version: 2,
};

const correctedHash = generateHash(correctedRecord);

const correctionTx =
  await registry.write.registerRecord([
    recordRef,
    2n,
    correctedHash,
  ]);

const correctionReceipt =
  await publicClient.waitForTransactionReceipt({
    hash: correctionTx,
  });

if (correctionReceipt.status !== "success") {
  throw new Error("Correction transaction failed");
}

console.log("Correction transaction:", correctionTx);

// 6. Verify both versions
console.log("\n========== VERSION HISTORY ==========");

const latestVersion =
  await registry.read.getLatestVersion([recordRef]);

const version1Verified =
  await registry.read.verifyRecord([
    recordRef,
    1n,
    originalHash,
  ]);

const version2Verified =
  await registry.read.verifyRecord([
    recordRef,
    2n,
    correctedHash,
  ]);

console.log("Latest version:", latestVersion.toString());
console.log("Version 1 verified:", version1Verified);
console.log("Version 2 verified:", version2Verified);

console.log("\n========== DEMO COMPLETE ==========");