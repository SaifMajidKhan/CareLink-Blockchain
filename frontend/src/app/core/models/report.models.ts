import { MedicationAnchor } from './medication.models';

export interface ReportCreate {
  prediction_id: number;
}

export interface MedicalReport {
  id: number;
  patient_id: number;
  prediction_id: number;
  record_ref: string;
  version: number;
  file_name: string;
  created_at: string;
  download_url: string;
}

export interface ReportWithAnchor {
  report: MedicalReport;
  blockchain: MedicationAnchor | null;
}

export interface ReportIntegrity {
  report_id: number;
  record_ref: string;
  version: number;
  status: string;
  verified: boolean | null;
}