import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import {
  catchError,
  forkJoin,
  of
} from 'rxjs';

import { API_BASE_URL } from '../config/api.config';

import {
  PatientSummary,
  PredictionEntry,
  ReportEntry
} from '../models/dashboard.models';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  private readonly http = inject(HttpClient);

  private getList<T>(path: string) {

    return this.http
      .get<T[]>(`${API_BASE_URL}${path}`)
      .pipe(
        catchError(() => of(null))
      );

  }

  getOverview() {

    return forkJoin({
      patients: this.getList<PatientSummary>(
        '/patients/'
      ),

      medications: this.getList<unknown>(
        '/medications/'
      ),

      predictions: this.getList<PredictionEntry>(
        '/predictions/'
      ),

      reports: this.getList<ReportEntry>(
        '/reports/'
      )
    });

  }

}