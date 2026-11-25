import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, forkJoin, of } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';

export interface ServiceHealth {
  status: string;
  service?: string;
  connected?: boolean;
  chain_id?: number;
  contract_address?: string;
  writer_authorized?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class HealthService {

  private readonly http = inject(HttpClient);

  private checkEndpoint(path: string) {

    return this.http
      .get<ServiceHealth>(`${API_BASE_URL}${path}`)
      .pipe(
        catchError(() =>
          of<ServiceHealth>({
            status: 'unavailable',
            connected: false
          })
        )
      );

  }

  getSystemHealth() {

    return forkJoin({
      backend: this.checkEndpoint('/health'),
      database: this.checkEndpoint('/health/database'),
      blockchain: this.checkEndpoint('/health/blockchain')
    });

  }

}