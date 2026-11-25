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

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import {
  LucideAngularModule,
  Brain,
  ShieldCheck,
  ShieldAlert,
  Activity,
  RefreshCw,
  History,
  Save,
  Eye,
  X,
  Copy,
  Info
} from 'lucide-angular';

import {
  PredictionService
} from '../../core/services/prediction';

import {
  PatientService
} from '../../core/services/patient';

import {
  Patient
} from '../../core/models/patient.models';

import {
  PredictionFeatures,
  PredictionResult,
  PredictionWithAnchor,
  PredictionIntegrity
} from '../../core/models/prediction.models';

import {
  StatusBadge
} from '../../shared/components/status-badge/status-badge';

@Component({
  selector: 'app-predictions',
  imports: [
    DatePipe,
    DecimalPipe,
    ReactiveFormsModule,
    LucideAngularModule,
    StatusBadge
  ],
  templateUrl: './predictions.html',
  styleUrl: './predictions.scss'
})
export class Predictions implements OnInit {

  private readonly fb = inject(FormBuilder);

  private readonly predictionService =
    inject(PredictionService);

  private readonly patientService =
    inject(PatientService);

  readonly Brain = Brain;
  readonly ShieldCheck = ShieldCheck;
  readonly ShieldAlert = ShieldAlert;
  readonly Activity = Activity;
  readonly RefreshCw = RefreshCw;
  readonly History = History;
  readonly Save = Save;
  readonly Eye = Eye;
  readonly X = X;
  readonly Copy = Copy;
  readonly Info = Info;

  readonly patients = signal<Patient[]>([]);

  readonly predictions =
    signal<PredictionWithAnchor[]>([]);

  readonly result =
    signal<PredictionResult | null>(null);

  readonly selected =
    signal<PredictionWithAnchor | null>(null);

  readonly integrity =
    signal<PredictionIntegrity | null>(null);

  readonly busy = signal(false);
  readonly loading = signal(true);
  readonly error = signal('');
  readonly historyError = signal('');
  readonly detailError = signal('');
  readonly notice = signal('');
  readonly copied = signal('');

  readonly resultMode =
    signal<'preview' | 'registered' | null>(null);

  readonly patientFilter = signal<number | undefined>(
    undefined
  );

  readonly form = this.fb.nonNullable.group({

    patient_id: [
      0,
      [Validators.required, Validators.min(1)]
    ],

    age: [
      45,
      [Validators.required, Validators.min(18), Validators.max(85)]
    ],

    daily_doses: [
      2,
      [Validators.required, Validators.min(1), Validators.max(4)]
    ],

    missed_doses_7d: [
      2,
      [Validators.required, Validators.min(0), Validators.max(28)]
    ],

    adherence_percent: [
      80,
      [Validators.required, Validators.min(0), Validators.max(100)]
    ],

    reminder_percent: [
      80,
      [Validators.required, Validators.min(0), Validators.max(100)]
    ],

    medication_count: [
      2,
      [Validators.required, Validators.min(1), Validators.max(6)]
    ],

    chronic_condition_count: [
      1,
      [Validators.required, Validators.min(1), Validators.max(3)]
    ],

    previous_non_adherence: [0]

  });

  readonly highRiskCount = computed(() =>
    this.predictions().filter(
      item => item.prediction.risk_level === 'High'
    ).length
  );

  readonly registeredCount = computed(() =>
    this.predictions().filter(
      item => item.blockchain?.status === 'registered'
    ).length
  );

  readonly riskColor = computed(() => {

    switch (this.result()?.risk_level) {

      case 'High':
        return '#dc2626';

      case 'Medium':
        return '#d97706';

      case 'Low':
        return '#15803d';

      default:
        return '#94a3b8';

    }

  });

  constructor() {

    this.form.valueChanges.subscribe(() => {

      this.result.set(null);
      this.resultMode.set(null);
      this.notice.set('');
      this.error.set('');

    });

  }

  ngOnInit(): void {

    this.patientService.getPatients().subscribe({

      next: patients => {

        this.patients.set(patients);

        if (patients.length > 0) {

          this.form.patchValue({
            patient_id: patients[0].id,
            age: patients[0].age
          });

        }

      },

      error: () => {

        this.error.set('Unable to retrieve patients.');

      }

    });

    this.loadHistory();

  }

  patientName(id: number): string {

    return this.patients().find(
      patient => patient.id === id
    )?.name ?? `Patient #${id}`;

  }

  onPatientChange(): void {

    const patient = this.patients().find(
      item => item.id === this.form.controls.patient_id.value
    );

    if (patient) {

      this.form.controls.age.setValue(patient.age);

    }

  }

  loadHistory(): void {

    this.loading.set(true);
    this.historyError.set('');

    this.predictionService.getPredictions(
      this.patientFilter()
    ).subscribe({

      next: records => {

        this.predictions.set(records);
        this.loading.set(false);

      },

      error: () => {

        this.predictions.set([]);
        this.historyError.set(
          'Unable to retrieve prediction history.'
        );
        this.loading.set(false);

      }

    });

  }

  changeFilter(value: string): void {

    this.patientFilter.set(
      value ? Number(value) : undefined
    );

    this.loadHistory();

  }

  loadDemo(level: 'low' | 'high'): void {

    if (this.busy()) return;

    const patient = this.patients().find(
      item => item.id === this.form.controls.patient_id.value
    );

    this.form.patchValue({

      age: patient?.age ?? 45,

      daily_doses: level === 'high' ? 4 : 1,

      missed_doses_7d: level === 'high' ? 18 : 0,

      adherence_percent: level === 'high' ? 40 : 98,

      reminder_percent: level === 'high' ? 20 : 95,

      medication_count: level === 'high' ? 6 : 1,

      chronic_condition_count: level === 'high' ? 3 : 1,

      previous_non_adherence: level === 'high' ? 1 : 0

    });

  }

  private getFeatures(): PredictionFeatures | null {

    this.error.set('');

    if (this.form.invalid) {

      this.form.markAllAsTouched();

      this.error.set(
        'Please complete all fields within their allowed ranges.'
      );

      return null;

    }

    const values = this.form.getRawValue();

    const integerFields = [
      values.age,
      values.daily_doses,
      values.missed_doses_7d,
      values.medication_count,
      values.chronic_condition_count
    ];

    if (integerFields.some(value => !Number.isInteger(value))) {

      this.error.set('Dose and count fields must be whole numbers.');

      return null;

    }

    if (
      values.missed_doses_7d >
      values.daily_doses * 7
    ) {

      this.error.set(
        'Missed doses cannot exceed total scheduled weekly doses.'
      );

      return null;

    }

    return {

      age: values.age,

      daily_doses: values.daily_doses,

      missed_doses_7d: values.missed_doses_7d,

      adherence_rate_30d:
        values.adherence_percent / 100,

      reminder_response_rate:
        values.reminder_percent / 100,

      medication_count: values.medication_count,

      chronic_condition_count:
        values.chronic_condition_count,

      previous_non_adherence:
        values.previous_non_adherence === 1 ? 1 : 0

    };

  }

  preview(): void {

    if (this.busy()) return;

    const features = this.getFeatures();

    if (!features) return;

    this.busy.set(true);
    this.result.set(null);
    this.resultMode.set(null);
    this.notice.set('');

    this.predictionService.preview(features).subscribe({

      next: result => {

        this.result.set(result);
        this.resultMode.set('preview');

        this.notice.set(
          'Preview generated. No prediction record has been saved.'
        );

        this.busy.set(false);

      },

      error: response => {

        this.error.set(
          this.errorText(response, 'AI prediction unavailable.')
        );

        this.busy.set(false);

      }

    });

  }

  register(): void {

    if (this.busy()) return;

    const features = this.getFeatures();

    if (!features) return;

    this.busy.set(true);
    this.result.set(null);
    this.resultMode.set(null);
    this.notice.set('');

    this.predictionService.createPrediction({

      patient_id: this.form.controls.patient_id.value,
      features

    }).subscribe({

      next: record => {

        this.result.set(record.prediction);
        this.resultMode.set('registered');

        this.notice.set(
          `Assessment #${record.prediction.id} saved. ` +
          `Blockchain status: ${record.blockchain?.status ?? 'unavailable'}.`
        );

        this.busy.set(false);
        this.loadHistory();
        this.showDetails(record);

      },

      error: response => {

        this.error.set(
          this.errorText(
            response,
            'Unable to register assessment. Refresh history before retrying.'
          )
        );

        this.busy.set(false);

      }

    });

  }

  showDetails(record: PredictionWithAnchor): void {

    if (this.busy()) return;

    this.selected.set(record);
    this.integrity.set(null);
    this.detailError.set('');
    this.copied.set('');

  }

  closeDetails(): void {

    if (this.busy()) return;

    this.selected.set(null);
    this.integrity.set(null);

  }

  verify(): void {

    const record = this.selected();

    if (!record || this.busy()) return;

    this.busy.set(true);
    this.detailError.set('');
    this.integrity.set(null);

    this.predictionService.verifyIntegrity(
      record.prediction.id
    ).subscribe({

      next: result => {

        this.integrity.set(result);
        this.busy.set(false);

      },

      error: response => {

        this.detailError.set(
          this.errorText(response, 'Verification unavailable.')
        );

        this.busy.set(false);

      }

    });

  }

  retry(): void {

    const record = this.selected();

    if (!record || this.busy()) return;

    this.busy.set(true);
    this.detailError.set('');
    this.integrity.set(null);

    this.predictionService.retryAnchor(
      record.prediction.id
    ).subscribe({

      next: anchor => {

        this.selected.set({
          prediction: record.prediction,
          blockchain: anchor
        });

        this.busy.set(false);
        this.loadHistory();

      },

      error: response => {

        this.detailError.set(
          this.errorText(response, 'Registration retry failed.')
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