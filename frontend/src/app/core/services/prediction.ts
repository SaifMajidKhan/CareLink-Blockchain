import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { API_BASE_URL } from '../config/api.config';

import {
  PredictionFeatures,
  PredictionCreate,
  PredictionResult,
  PredictionWithAnchor,
  PredictionIntegrity
} from '../models/prediction.models';

import { MedicationAnchor } from '../models/medication.models';

@Injectable({
  providedIn: 'root'
})
export class PredictionService {

  private readonly http = inject(HttpClient);

  private readonly url =
    `${API_BASE_URL}/predictions`;

  preview(features: PredictionFeatures) {

    return this.http.post<PredictionResult>(
      `${this.url}/preview`,
      features
    );

  }

  createPrediction(payload: PredictionCreate) {

    return this.http.post<PredictionWithAnchor>(
      `${this.url}/`,
      payload
    );

  }

  getPredictions(patientId?: number) {

    let params = new HttpParams();

    if (patientId !== undefined) {
      params = params.set('patient_id', patientId);
    }

    return this.http.get<PredictionWithAnchor[]>(
      `${this.url}/`,
      { params }
    );

  }

  getPrediction(id: number) {

    return this.http.get<PredictionWithAnchor>(
      `${this.url}/${id}`
    );

  }

  verifyIntegrity(id: number) {

    return this.http.get<PredictionIntegrity>(
      `${this.url}/${id}/integrity`
    );

  }

  retryAnchor(id: number) {

    return this.http.post<MedicationAnchor>(
      `${this.url}/${id}/retry-anchor`,
      null
    );

  }

}