import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { API_BASE_URL } from '../config/api.config';

import {
  Medication,
  MedicationWithAnchor
} from '../models/medication.models';

import {
  AnchorSummary
} from '../models/dashboard.models';

@Injectable({
  providedIn: 'root'
})
export class MedicationService {

  private readonly http = inject(HttpClient);

  private readonly url =
    `${API_BASE_URL}/medications`;

  getMedications(
    patientId?: number,
    skip = 0,
    limit = 100
  ) {

    let params = new HttpParams()
      .set('skip', skip)
      .set('limit', limit);

    if (patientId !== undefined) {
      params = params.set('patient_id', patientId);
    }

    return this.http.get<Medication[]>(
      `${this.url}/`,
      { params }
    );

  }

  getMedication(id: number) {

    return this.http.get<MedicationWithAnchor>(
      `${this.url}/${id}`
    );

  }

  verifyIntegrity(id: number) {

    return this.http.get<Record<string, unknown>>(
      `${this.url}/${id}/integrity`
    );

  }

  retryAnchor(id: number) {

    return this.http.post<AnchorSummary>(
      `${this.url}/${id}/retry-anchor`,
      null
    );

  }

  getHistory(id: number) {

    return this.http.get<MedicationWithAnchor[]>(
      `${this.url}/${id}/history`
    );

  }

}