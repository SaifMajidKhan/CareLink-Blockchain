import { AnchorSummary } from './dashboard.models';

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

export interface MedicationWithAnchor {
  medication: Medication;
  blockchain: AnchorSummary;
}