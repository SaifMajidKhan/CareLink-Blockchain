import { MedicationAnchor } from './medication.models';

export type EntityType =
  | 'medication_event'
  | 'ai_prediction'
  | 'medical_report';

export interface BlockchainAnchor extends MedicationAnchor {
  id: number;
  entity_type: EntityType;
  entity_id: number;
  serialization_version: number;
  created_at: string;
}

export interface BlockchainSummary {
  total: number;
  registered: number;
  pending: number;
  failed: number;
  medication_events: number;
  ai_predictions: number;
  medical_reports: number;
}

export interface BlockchainAnchorPage {
  items: BlockchainAnchor[];
  total: number;
  skip: number;
  limit: number;
}

export interface BlockchainVerification {
  anchor_id: number;
  record_ref: string;
  version: number;
  status: string;
  verified: boolean | null;
  message: string;
}