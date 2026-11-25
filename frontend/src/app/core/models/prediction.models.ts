import { MedicationAnchor } from './medication.models';

export type RiskLevel = 'Low' | 'Medium' | 'High';

export interface PredictionFeatures {
  age: number;
  daily_doses: number;
  missed_doses_7d: number;
  adherence_rate_30d: number;
  reminder_response_rate: number;
  medication_count: number;
  chronic_condition_count: number;
  previous_non_adherence: 0 | 1;
}

export interface PredictionCreate {
  patient_id: number;
  features: PredictionFeatures;
}

export interface PredictionResult {
  risk_score: number;
  risk_level: RiskLevel;
  model_version: string;
  model_sha256: string;
  algorithm: string;
  dataset_type: string;
  disclaimer: string;
}

export interface Prediction extends PredictionResult {
  id: number;
  patient_id: number;
  record_ref: string;
  version: number;
  input_features: PredictionFeatures;
  created_at: string;
}

export interface PredictionWithAnchor {
  prediction: Prediction;
  blockchain: MedicationAnchor | null;
}

export interface PredictionIntegrity {
  prediction_id: number;
  record_ref: string;
  version: number;
  status: string;
  verified: boolean | null;
}