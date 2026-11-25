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

import { forkJoin } from 'rxjs';

import {
  LucideAngularModule,
  FileText,
  FilePlus,
  Download,
  UploadCloud,
  ShieldCheck,
  ShieldAlert,
  RefreshCw,
  Eye,
  X,
  Copy,
  Info
} from 'lucide-angular';

import { ReportService } from '../../core/services/report';
import { PatientService } from '../../core/services/patient';
import { PredictionService } from '../../core/services/prediction';

import { Patient } from '../../core/models/patient.models';

import {
  PredictionWithAnchor
} from '../../core/models/prediction.models';

import {
  ReportWithAnchor,
  ReportIntegrity
} from '../../core/models/report.models';

import {
  StatusBadge
} from '../../shared/components/status-badge/status-badge';

@Component({
  selector: 'app-reports',
  imports: [
    DatePipe,
    DecimalPipe,
    LucideAngularModule,
    StatusBadge
  ],
  templateUrl: './reports.html',
  styleUrl: './reports.scss'
})
export class Reports implements OnInit {

  private readonly reportService =
    inject(ReportService);

  private readonly patientService =
    inject(PatientService);

  private readonly predictionService =
    inject(PredictionService);

  readonly FileText = FileText;
  readonly FilePlus = FilePlus;
  readonly Download = Download;
  readonly UploadCloud = UploadCloud;
  readonly ShieldCheck = ShieldCheck;
  readonly ShieldAlert = ShieldAlert;
  readonly RefreshCw = RefreshCw;
  readonly Eye = Eye;
  readonly X = X;
  readonly Copy = Copy;
  readonly Info = Info;

  readonly patients = signal<Patient[]>([]);

  readonly predictions =
    signal<PredictionWithAnchor[]>([]);

  readonly reports =
    signal<ReportWithAnchor[]>([]);

  readonly patientId = signal(0);
  readonly predictionId = signal(0);
  readonly verificationReportId = signal(0);

  readonly selectedFile = signal<File | null>(null);

  readonly selected =
    signal<ReportWithAnchor | null>(null);

  readonly integrity =
    signal<ReportIntegrity | null>(null);

  readonly loading = signal(true);
  readonly busy = signal(false);

  readonly generationError = signal('');
  readonly verificationError = signal('');
  readonly listError = signal('');
  readonly detailError = signal('');
  readonly notice = signal('');
  readonly copied = signal('');

  readonly filteredPredictions = computed(() =>
    this.predictions().filter(item =>
      item.prediction.patient_id === this.patientId()
    )
  );

  readonly selectedPrediction = computed(() =>
    this.filteredPredictions().find(item =>
      item.prediction.id === this.predictionId()
    ) ?? null
  );

  readonly registeredCount = computed(() =>
    this.reports().filter(item =>
      item.blockchain?.status === 'registered'
    ).length
  );

  readonly pendingCount = computed(() =>
    this.reports().filter(item =>
      item.blockchain?.status !== 'registered'
    ).length
  );

  ngOnInit(): void {

    this.loadData();

  }

  loadData(): void {

    this.loading.set(true);
    this.listError.set('');

    forkJoin({

      patients: this.patientService.getPatients(),

      predictions:
        this.predictionService.getPredictions(),

      reports: this.reportService.getReports()

    }).subscribe({

      next: data => {

        this.patients.set(data.patients);
        this.predictions.set(data.predictions);
        this.reports.set(data.reports);

        if (!data.patients.some(
          patient => patient.id === this.patientId()
        )) {

          this.patientId.set(
            data.patients[0]?.id ?? 0
          );

        }

        if (!this.filteredPredictions().some(
          item => item.prediction.id === this.predictionId()
        )) {

          this.predictionId.set(
            this.filteredPredictions()[0]?.prediction.id ?? 0
          );

        }

        if (!data.reports.some(
          item => item.report.id === this.verificationReportId()
        )) {

          this.verificationReportId.set(
            data.reports[0]?.report.id ?? 0
          );

          this.integrity.set(null);

        }

        this.loading.set(false);

      },

      error: () => {

        this.listError.set(
          'Unable to retrieve report data. Please refresh.'
        );

        this.loading.set(false);

      }

    });

  }

  patientName(id: number): string {

    return this.patients().find(
      patient => patient.id === id
    )?.name ?? `Patient #${id}`;

  }

  changePatient(value: string): void {

    this.patientId.set(Number(value));

    this.predictionId.set(
      this.filteredPredictions()[0]?.prediction.id ?? 0
    );

    this.generationError.set('');
    this.notice.set('');

  }

  changePrediction(value: string): void {

    this.predictionId.set(Number(value));
    this.generationError.set('');
    this.notice.set('');

  }

  generate(): void {

    if (this.busy()) return;

    this.generationError.set('');
    this.notice.set('');

    const prediction = this.selectedPrediction();

    if (!prediction) {

      this.generationError.set(
        'Please select a saved AI assessment.'
      );

      return;

    }

    if (prediction.blockchain?.status !== 'registered') {

      this.generationError.set(
        'The assessment must have a registered blockchain fingerprint.'
      );

      return;

    }

    this.busy.set(true);

    this.reportService.generateReport({

      prediction_id: prediction.prediction.id

    }).subscribe({

      next: result => {

        this.busy.set(false);

        this.notice.set(
          `Report #${result.report.id} generated. ` +
          `Blockchain status: ${result.blockchain?.status ?? 'unavailable'}.`
        );

        this.verificationReportId.set(result.report.id);
        this.selectedFile.set(null);
        this.integrity.set(null);

        this.loadData();
        this.showDetails(result);

      },

      error: response => {

        this.generationError.set(
          this.errorText(
            response,
            'Report generation failed. Refresh before retrying.'
          )
        );

        this.busy.set(false);

      }

    });

  }

  download(record: ReportWithAnchor): void {

    if (this.busy()) return;

    this.busy.set(true);
    this.listError.set('');
    this.detailError.set('');

    this.reportService.downloadReport(
      record.report.id
    ).subscribe({

      next: blob => {

        const url = URL.createObjectURL(blob);

        const link = document.createElement('a');

        link.href = url;
        link.download = record.report.file_name;

        document.body.appendChild(link);
        link.click();
        link.remove();

        setTimeout(
          () => URL.revokeObjectURL(url),
          1000
        );

        this.busy.set(false);

      },

      error: () => {

        const message = 'Unable to download report file.';

        if (this.selected()) {
          this.detailError.set(message);
        } else {
          this.listError.set(message);
        }

        this.busy.set(false);

      }

    });

  }

  changeVerificationReport(value: string): void {

    this.verificationReportId.set(Number(value));
    this.integrity.set(null);
    this.verificationError.set('');

  }

  selectFile(event: Event): void {

    const input = event.target as HTMLInputElement;

    const file = input.files?.[0];

    this.integrity.set(null);
    this.verificationError.set('');
    this.selectedFile.set(null);

    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {

      this.verificationError.set(
        'Please select a PDF document.'
      );

      input.value = '';
      return;

    }

    if (file.size > 10 * 1024 * 1024) {

      this.verificationError.set(
        'Maximum file size is 10 MB.'
      );

      input.value = '';
      return;

    }

    this.selectedFile.set(file);

    input.value = '';

  }

  verify(): void {

    if (this.busy()) return;

    this.verificationError.set('');
    this.integrity.set(null);

    const file = this.selectedFile();

    const id = this.verificationReportId();

    if (!id || !file) {

      this.verificationError.set(
        'Select a registered report and a PDF document.'
      );

      return;

    }

    this.busy.set(true);

    this.reportService.verifyReport(
      id,
      file
    ).subscribe({

      next: result => {

        this.integrity.set(result);
        this.busy.set(false);

      },

      error: response => {

        this.verificationError.set(
          this.errorText(
            response,
            'Document verification unavailable.'
          )
        );

        this.busy.set(false);

      }

    });

  }

  prepareVerification(record: ReportWithAnchor): void {

    if (this.busy()) return;

    this.verificationReportId.set(record.report.id);

    this.selectedFile.set(null);
    this.integrity.set(null);
    this.verificationError.set('');

    this.selected.set(null);

    document.getElementById('verify-document')
      ?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });

  }

  showDetails(record: ReportWithAnchor): void {

    if (this.busy()) return;

    this.selected.set(record);
    this.detailError.set('');
    this.copied.set('');

  }

  closeDetails(): void {

    if (this.busy()) return;

    this.selected.set(null);

  }

  retry(): void {

    const record = this.selected();

    if (!record || this.busy()) return;

    this.busy.set(true);
    this.detailError.set('');

    this.reportService.retryAnchor(
      record.report.id
    ).subscribe({

      next: anchor => {

        this.selected.set({
          report: record.report,
          blockchain: anchor
        });

        this.busy.set(false);
        this.loadData();

      },

      error: response => {

        this.detailError.set(
          this.errorText(
            response,
            'Registration retry failed.'
          )
        );

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

  private errorText(
    response: any,
    fallback: string
  ): string {

    return typeof response.error?.detail === 'string'
      ? response.error.detail
      : fallback;

  }

}