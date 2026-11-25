export type MedicationStatus =
  'Taken' | 'Missed' | 'Pending';

export interface Medication {
  id: number;
  patient_id: number;
  record_ref: string;
  version: number;
  medication_name: string;
  dosage: string;
  status: MedicationStatus;
  scheduled_at: string;
  recorded_at: string;
}

export interface MedicationCorrection {
  medication_name: string;
  dosage: string;
  status: MedicationStatus;
  scheduled_at: string;
}

export interface MedicationCreate
  extends MedicationCorrection {
  patient_id: number;
}

export interface MedicationAnchor {
  record_ref: string;
  version: number;
  fingerprint: string;
  transaction_hash: string | null;
  block_number: number | null;
  chain_id: number;
  contract_address: string;
  status: string;
  retry_count: number;
  anchored_at: string | null;
}

export interface MedicationWithAnchor {
  medication: Medication;
  blockchain: MedicationAnchor;
}

export interface MedicationIntegrity {
  medication_id: number;
  record_ref: string;
  version: number;
  status: string;
  verified: boolean | null;
  message: string;
}