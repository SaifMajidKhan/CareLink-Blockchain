import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';

import { API_BASE_URL } from '../config/api.config';

import {
  BlockchainSummary,
  BlockchainAnchorPage,
  BlockchainAnchor,
  BlockchainVerification
} from '../models/blockchain.models';

@Injectable({ providedIn: 'root' })
export class BlockchainService {

  private readonly http = inject(HttpClient);
  private readonly url = `${API_BASE_URL}/blockchain`;

  getSummary() {
    return this.http.get<BlockchainSummary>(
      `${this.url}/summary`
    );
  }

  getAnchors(
    search = '',
    entityType = '',
    status = '',
    skip = 0,
    limit = 10
  ) {

    let params = new HttpParams()
      .set('skip', skip)
      .set('limit', limit);

    if (search.trim()) {
      params = params.set('search', search.trim());
    }

    if (entityType) {
      params = params.set('entity_type', entityType);
    }

    if (status) {
      params = params.set('status', status);
    }

    return this.http.get<BlockchainAnchorPage>(
      `${this.url}/anchors`,
      { params }
    );

  }

  getAnchor(id: number) {
    return this.http.get<BlockchainAnchor>(
      `${this.url}/anchors/${id}`
    );
  }

  verifyAnchor(id: number) {
    return this.http.get<BlockchainVerification>(
      `${this.url}/anchors/${id}/verify`
    );
  }

}