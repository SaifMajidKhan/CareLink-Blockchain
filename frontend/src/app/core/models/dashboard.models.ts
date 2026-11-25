export interface PatientSummary {
  id: number;
  name: string;
  age: number;
  condition: string;
  created_at: string;
}

export interface AnchorSummary {
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

export interface PredictionSummary {
  id: number;
  patient_id: number;
  risk_score: number;
  risk_level: string;
  model_version: string;
  algorithm: string;
  dataset_type: string;
  created_at: string;
}

export interface PredictionEntry {
  prediction: PredictionSummary;
  blockchain: AnchorSummary | null;
}

export interface ReportEntry {
  report: {
    id: number;
    patient_id: number;
    prediction_id: number;
    file_name: string;
    created_at: string;
  };
  blockchain: AnchorSummary | null;
}