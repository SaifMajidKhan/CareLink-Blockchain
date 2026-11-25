import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { API_BASE_URL } from '../config/api.config';

import {
  Patient,
  PatientCreate
} from '../models/patient.models';

@Injectable({
  providedIn: 'root'
})
export class PatientService {

  private readonly http = inject(HttpClient);

  getPatients(skip = 0, limit = 100) {

    return this.http.get<Patient[]>(
      `${API_BASE_URL}/patients/`,
      {
        params: {
          skip,
          limit
        }
      }
    );

  }

  getPatient(id: number) {

    return this.http.get<Patient>(
      `${API_BASE_URL}/patients/${id}`
    );

  }

  createPatient(payload: PatientCreate) {

    return this.http.post<Patient>(
      `${API_BASE_URL}/patients/`,
      payload
    );

  }

}