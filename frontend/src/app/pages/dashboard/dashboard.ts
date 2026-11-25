import {
  Component,
  computed,
  inject,
  OnInit,
  signal
} from '@angular/core';

import {
  DatePipe,
  DecimalPipe
} from '@angular/common';

import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import {
  LucideAngularModule,
  Users,
  Pill,
  BrainCircuit,
  FileText,
  RefreshCw,
  ShieldCheck,
  ArrowUpRight,
  Activity
} from 'lucide-angular';

import {
  HealthService,
  ServiceHealth
} from '../../core/services/health';

import {
  DashboardService
} from '../../core/services/dashboard';

import {
  PatientSummary,
  PredictionEntry,
  ReportEntry
} from '../../core/models/dashboard.models';

import {
  StatCard
} from '../../shared/components/stat-card/stat-card';

import {
  StatusBadge
} from '../../shared/components/status-badge/status-badge';

@Component({
  selector: 'app-dashboard',
  imports: [
    RouterLink,
    DatePipe,
    DecimalPipe,
    LucideAngularModule,
    StatCard,
    StatusBadge
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {

  private readonly healthService = inject(HealthService);

  private readonly dashboardService = inject(
    DashboardService
  );

  readonly Users = Users;
  readonly Pill = Pill;
  readonly BrainCircuit = BrainCircuit;
  readonly FileText = FileText;
  readonly RefreshCw = RefreshCw;
  readonly ShieldCheck = ShieldCheck;
  readonly ArrowUpRight = ArrowUpRight;
  readonly Activity = Activity;

  readonly loading = signal(true);

  readonly patients = signal<PatientSummary[] | null>(
    null
  );

  readonly medications = signal<unknown[] | null>(
    null
  );

  readonly predictions = signal<PredictionEntry[] | null>(
    null
  );

  readonly reports = signal<ReportEntry[] | null>(
    null
  );

  readonly health = signal<{
    backend: ServiceHealth;
    database: ServiceHealth;
    blockchain: ServiceHealth;
  } | null>(null);

  readonly lastUpdated = signal<Date | null>(null);

  readonly latestPrediction = computed(() =>
    this.predictions()?.[0] ?? null
  );

  readonly latestPatientName = computed(() => {

    const patientId =
      this.latestPrediction()?.prediction.patient_id;

    return this.patients()?.find(
      patient => patient.id === patientId
    )?.name ?? `Patient #${patientId ?? '—'}`;

  });

  readonly dataUnavailable = computed(() =>
    this.patients() === null ||
    this.medications() === null ||
    this.predictions() === null ||
    this.reports() === null
  );

  readonly recentAnchors = computed(() => {

    const predictions = (
      this.predictions() ?? []
    ).map(item => ({
      type: 'AI prediction',
      id: item.prediction.id,
      anchor: item.blockchain
    }));

    const reports = (
      this.reports() ?? []
    ).map(item => ({
      type: 'Medical report',
      id: item.report.id,
      anchor: item.blockchain
    }));

    return [...predictions, ...reports]
      .filter(item => item.anchor !== null)
      .sort((a, b) =>
        (b.anchor?.block_number ?? 0) -
        (a.anchor?.block_number ?? 0)
      )
      .slice(0, 5);

  });

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {

    this.loading.set(true);

    forkJoin({
      health: this.healthService.getSystemHealth(),
      overview: this.dashboardService.getOverview()
    }).subscribe({

      next: ({ health, overview }) => {

        this.health.set(health);

        this.patients.set(overview.patients);
        this.medications.set(overview.medications);
        this.predictions.set(overview.predictions);
        this.reports.set(overview.reports);

        this.lastUpdated.set(new Date());

        this.loading.set(false);

      },

      error: () => {

        this.loading.set(false);

      }

    });

  }

  count(records: unknown[] | null): number | string {

    if (records === null) {
      return '—';
    }

    return records.length;

  }

  shortenHash(hash: string | null | undefined): string {

    if (!hash) {
      return '—';
    }

    return `${hash.slice(0, 10)}...${hash.slice(-6)}`;

  }

}