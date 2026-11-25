import {
  Component,
  computed,
  inject,
  OnInit,
  signal
} from '@angular/core';

import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';

import {
  LucideAngularModule,
  Blocks,
  ShieldCheck,
  ShieldAlert,
  Search,
  RefreshCw,
  Copy,
  Eye,
  X,
  Info,
  ArrowLeft,
  ArrowRight
} from 'lucide-angular';

import {
  BlockchainService
} from '../../core/services/blockchain';

import {
  HealthService,
  ServiceHealth
} from '../../core/services/health';

import {
  BlockchainAnchor,
  BlockchainSummary,
  BlockchainVerification
} from '../../core/models/blockchain.models';

import {
  StatusBadge
} from '../../shared/components/status-badge/status-badge';

@Component({
  selector: 'app-blockchain',
  imports: [
    DatePipe,
    RouterLink,
    LucideAngularModule,
    StatusBadge
  ],
  templateUrl: './blockchain.html',
  styleUrl: './blockchain.scss'
})
export class Blockchain implements OnInit {

  private readonly service = inject(BlockchainService);
  private readonly healthService = inject(HealthService);

  readonly Blocks = Blocks;
  readonly ShieldCheck = ShieldCheck;
  readonly ShieldAlert = ShieldAlert;
  readonly Search = Search;
  readonly RefreshCw = RefreshCw;
  readonly Copy = Copy;
  readonly Eye = Eye;
  readonly X = X;
  readonly Info = Info;
  readonly ArrowLeft = ArrowLeft;
  readonly ArrowRight = ArrowRight;

  readonly summary = signal<BlockchainSummary | null>(null);
  readonly health = signal<ServiceHealth | null>(null);
  readonly anchors = signal<BlockchainAnchor[]>([]);

  readonly selected = signal<BlockchainAnchor | null>(null);

  readonly verification =
    signal<BlockchainVerification | null>(null);

  readonly search = signal('');
  readonly entityType = signal('');
  readonly status = signal('');

  readonly loading = signal(true);
  readonly busy = signal(false);

  readonly error = signal('');
  readonly summaryError = signal('');
  readonly detailError = signal('');
  readonly copied = signal('');

  readonly page = signal(1);
  readonly total = signal(0);

  readonly pageSize = 10;

  readonly totalPages = computed(() =>
    Math.max(1, Math.ceil(this.total() / this.pageSize))
  );

  readonly distribution = computed(() => {

    const summary = this.summary();

    const total = summary?.total || 1;

    return [
      {
        label: 'Medication events',
        count: summary?.medication_events ?? 0,
        percent: (summary?.medication_events ?? 0) / total * 100,
        color: '#0f766e'
      },
      {
        label: 'AI predictions',
        count: summary?.ai_predictions ?? 0,
        percent: (summary?.ai_predictions ?? 0) / total * 100,
        color: '#8b5cf6'
      },
      {
        label: 'Medical reports',
        count: summary?.medical_reports ?? 0,
        percent: (summary?.medical_reports ?? 0) / total * 100,
        color: '#3b82f6'
      }
    ];

  });

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {

    this.summaryError.set('');

    this.service.getSummary().subscribe({
      next: summary => this.summary.set(summary),
      error: () => {
        this.summary.set(null);
        this.summaryError.set('Unable to retrieve registration statistics.');
      }
    });

    this.healthService.getSystemHealth().subscribe({
      next: health => this.health.set(health.blockchain),
      error: () => this.health.set({ status: 'unavailable' })
    });

    this.loadAnchors();

  }

  loadAnchors(): void {

    this.loading.set(true);
    this.error.set('');

    this.service.getAnchors(
      this.search(),
      this.entityType(),
      this.status(),
      (this.page() - 1) * this.pageSize,
      this.pageSize
    ).subscribe({

      next: result => {

        this.anchors.set(result.items);
        this.total.set(result.total);

        if (this.page() > this.totalPages()) {
          this.page.set(this.totalPages());
          this.loadAnchors();
          return;
        }

        this.loading.set(false);

      },

      error: () => {
        this.anchors.set([]);
        this.total.set(0);
        this.error.set('Unable to retrieve blockchain registrations.');
        this.loading.set(false);
      }

    });

  }

  applyFilters(): void {
    if (this.loading()) return;
    this.page.set(1);
    this.loadAnchors();
  }

  clearFilters(): void {

    this.search.set('');
    this.entityType.set('');
    this.status.set('');
    this.applyFilters();

  }

  changePage(page: number): void {

    if (
      this.loading() ||
      page < 1 ||
      page > this.totalPages()
    ) return;

    this.page.set(page);
    this.loadAnchors();

  }

  entityLabel(type: string): string {

    switch (type) {
      case 'medication_event':
        return 'Medication event';
      case 'ai_prediction':
        return 'AI prediction';
      case 'medical_report':
        return 'Medical report';
      default:
        return type;
    }

  }

  recordRoute(type: string): string {

    switch (type) {
      case 'medication_event':
        return '/medications';
      case 'ai_prediction':
        return '/predictions';
      case 'medical_report':
        return '/reports';
      default:
        return '/dashboard';
    }

  }

  shorten(value: string | null): string {

    if (!value) return '—';

    return value.length > 20
      ? `${value.slice(0, 10)}...${value.slice(-6)}`
      : value;

  }

  showDetails(anchor: BlockchainAnchor): void {

    if (this.busy()) return;

    this.selected.set(anchor);
    this.verification.set(null);
    this.detailError.set('');
    this.copied.set('');

  }

  closeDetails(): void {

    if (this.busy()) return;

    this.selected.set(null);
    this.verification.set(null);

  }

  verify(): void {

    const anchor = this.selected();

    if (!anchor || this.busy()) return;

    this.busy.set(true);
    this.detailError.set('');
    this.verification.set(null);

    this.service.verifyAnchor(anchor.id).subscribe({

      next: result => {
        this.verification.set(result);
        this.busy.set(false);
      },

      error: () => {
        this.detailError.set('Blockchain verification unavailable.');
        this.busy.set(false);
      }

    });

  }

  async copy(value: string): Promise<void> {

    try {

      await navigator.clipboard.writeText(value);
      this.copied.set('Copied to clipboard.');

    } catch {

      this.detailError.set('Unable to copy value.');

    }

  }

}