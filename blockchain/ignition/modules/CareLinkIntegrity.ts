import { buildModule } from
  "@nomicfoundation/hardhat-ignition/modules";

const CareLinkIntegrityModule = buildModule(
  "CareLinkIntegrityModule",
  (m) => {
    const registry = m.contract("CareLinkIntegrity");

    return { registry };
  }
);

export default CareLinkIntegrityModule;