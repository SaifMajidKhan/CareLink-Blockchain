import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { API_BASE_URL } from '../config/api.config';

import {
  Medication,
  MedicationCreate,
  MedicationCorrection,
  MedicationAnchor,
  MedicationWithAnchor,
  MedicationIntegrity
} from '../models/medication.models';

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

  createMedication(payload: MedicationCreate) {

    return this.http.post<MedicationWithAnchor>(
      `${this.url}/`,
      payload
    );

  }

  correctMedication(
    id: number,
    payload: MedicationCorrection
  ) {

    return this.http.post<MedicationWithAnchor>(
      `${this.url}/${id}/correct`,
      payload
    );

  }

  verifyIntegrity(id: number) {

    return this.http.get<MedicationIntegrity>(
      `${this.url}/${id}/integrity`
    );

  }

  retryAnchor(id: number) {

    return this.http.post<MedicationAnchor>(
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