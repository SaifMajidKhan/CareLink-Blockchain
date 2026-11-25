import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { API_BASE_URL } from '../config/api.config';

import {
  ReportCreate,
  ReportWithAnchor,
  ReportIntegrity
} from '../models/report.models';

import { MedicationAnchor } from '../models/medication.models';

@Injectable({
  providedIn: 'root'
})
export class ReportService {

  private readonly http = inject(HttpClient);

  private readonly url =
    `${API_BASE_URL}/reports`;

  getReports(patientId?: number) {

    let params = new HttpParams();

    if (patientId !== undefined) {
      params = params.set('patient_id', patientId);
    }

    return this.http.get<ReportWithAnchor[]>(
      `${this.url}/`,
      { params }
    );

  }

  getReport(id: number) {

    return this.http.get<ReportWithAnchor>(
      `${this.url}/${id}`
    );

  }

  generateReport(payload: ReportCreate) {

    return this.http.post<ReportWithAnchor>(
      `${this.url}/`,
      payload
    );

  }

  downloadReport(id: number) {

    return this.http.get(
      `${this.url}/${id}/download`,
      { responseType: 'blob' }
    );

  }

  verifyReport(id: number, file: File) {

    const formData = new FormData();

    formData.append('file', file, file.name);

    return this.http.post<ReportIntegrity>(
      `${this.url}/${id}/verify`,
      formData
    );

  }

  retryAnchor(id: number) {

    return this.http.post<MedicationAnchor>(
      `${this.url}/${id}/retry-anchor`,
      null
    );

  }

}