import {
  Component,
  computed,
  inject,
  OnInit,
  signal
} from '@angular/core';

import {
  DatePipe,
} from '@angular/common';

import { ActivatedRoute } from '@angular/router';
import { switchMap, of, catchError } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import {
  LucideAngularModule,
  Pill,
  CheckCircle,
  AlertCircle,
  Search,
  RefreshCw,
  ShieldCheck,
  History,
  X,
  Copy,
  Plus,
  Pencil,
  ShieldAlert
} from 'lucide-angular';

import {
  MedicationService
} from '../../core/services/medication';

import {
  PatientService
} from '../../core/services/patient';

import {
  Medication,
  MedicationWithAnchor,
  MedicationStatus,
  MedicationIntegrity,
  MedicationCorrection
} from '../../core/models/medication.models';

import {
  Patient
} from '../../core/models/patient.models';

import {
  StatCard
} from '../../shared/components/stat-card/stat-card';

import {
  StatusBadge
} from '../../shared/components/status-badge/status-badge';

@Component({
  selector: 'app-medications',
  imports: [
    DatePipe,
    LucideAngularModule,
    StatCard,
    ReactiveFormsModule,
    StatusBadge
  ],
  templateUrl: './medications.html',
  styleUrl: './medications.scss'
})
export class Medications implements OnInit {

  private readonly medicationService =
    inject(MedicationService);

  private readonly patientService =
    inject(PatientService);

    private readonly route = inject(ActivatedRoute);

    private readonly fb = inject(FormBuilder);

 readonly Plus = Plus;
 readonly Pencil = Pencil;
 readonly ShieldAlert = ShieldAlert;

 readonly formOpen = signal(false);
 readonly saving = signal(false);
 readonly formError = signal('');
 readonly notice = signal('');

 readonly correctionTarget =
  signal<Medication | null>(null);

 readonly medicationForm = this.fb.nonNullable.group({

  patient_id: [
    0,
    [
      Validators.required,
      Validators.min(1)
    ]
  ],

  medication_name: [
    '',
    [
      Validators.required,
      Validators.minLength(2),
      Validators.maxLength(150)
    ]
  ],

  dosage: [
    '',
    [
      Validators.required,
      Validators.maxLength(100)
    ]
  ],

  status: [
    'Pending' as MedicationStatus,
    Validators.required
  ],

  scheduled_at: [
    '',
    Validators.required
  ]

 });

  readonly Pill = Pill;
  readonly CheckCircle = CheckCircle;
  readonly AlertCircle = AlertCircle;
  readonly Search = Search;
  readonly RefreshCw = RefreshCw;
  readonly ShieldCheck = ShieldCheck;
  readonly History = History;
  readonly X = X;
  readonly Copy = Copy;

  readonly medications = signal<Medication[]>([]);
  readonly patients = signal<Patient[]>([]);

  readonly patientFilter = signal<number | undefined>(
    undefined
  );

  readonly statusFilter = signal('');
  readonly search = signal('');

  readonly loading = signal(true);
  readonly busy = signal(false);
  readonly error = signal('');
  readonly detailError = signal('');
  readonly message = signal('');

  readonly selected =
    signal<MedicationWithAnchor | null>(null);

  readonly history =
    signal<MedicationWithAnchor[]>([]);

  readonly integrity =
    signal<MedicationIntegrity | null>(null);

  readonly page = signal(1);
  readonly pageSize = 8;

  readonly takenCount = computed(() =>
    this.medications().filter(
      item => item.status === 'Taken'
    ).length
  );

  readonly missedCount = computed(() =>
    this.medications().filter(
      item => item.status === 'Missed'
    ).length
  );

  readonly filteredMedications = computed(() => {

    const query = this.search().trim().toLowerCase();
    const status = this.statusFilter();

    return this.medications().filter(item => {

      const matchesSearch =
        item.medication_name.toLowerCase().includes(query) ||
        item.dosage.toLowerCase().includes(query) ||
        this.patientName(item.patient_id)
          .toLowerCase().includes(query) ||
        String(item.id).includes(query);

      const matchesStatus =
        !status || item.status === status;

      return matchesSearch && matchesStatus;

    });

  });

  readonly totalPages = computed(() =>
    Math.max(
      1,
      Math.ceil(
        this.filteredMedications().length / this.pageSize
      )
    )
  );

  readonly visibleMedications = computed(() => {

    const start = (this.page() - 1) * this.pageSize;

    return this.filteredMedications().slice(
      start,
      start + this.pageSize
    );

  });

  constructor() {

    this.route.queryParamMap.pipe(

      switchMap(params => {

        const rawId = params.get('patient_id');
        const id = Number(rawId);

        this.patientFilter.set(
          rawId && Number.isInteger(id) && id > 0
            ? id
            : undefined
        );

        this.loading.set(true);
        this.error.set('');

        return this.medicationService.getMedications(
          this.patientFilter()
        ).pipe(
          catchError(() => {
            this.error.set(
              'Unable to retrieve medication records.'
            );
            return of([]);
          })
        );

      }),

      takeUntilDestroyed()

    ).subscribe(records => {

      this.medications.set(records);
      this.page.set(1);
      this.loading.set(false);

    });

  }

  ngOnInit(): void {

    this.patientService.getPatients().subscribe({
      next: patients => this.patients.set(patients)
    });

  }

  patientName(id: number): string {

    return this.patients().find(
      patient => patient.id === id
    )?.name ?? `Patient #${id}`;

  }

  loadMedications(): void {

    this.loading.set(true);
    this.error.set('');

    this.medicationService.getMedications(
      this.patientFilter()
    ).subscribe({

      next: records => {

        this.medications.set(records);
        this.page.set(1);
        this.loading.set(false);

      },

      error: () => {

        this.medications.set([]);
        this.error.set(
          'Unable to retrieve medication records.'
        );
        this.loading.set(false);

      }

    });

  }

  changePatient(value: string): void {

    this.patientFilter.set(
      value ? Number(value) : undefined
    );

    this.loadMedications();

  }

  changeSearch(value: string): void {

    this.search.set(value);
    this.page.set(1);

  }

  changeStatus(value: string): void {

    this.statusFilter.set(value);
    this.page.set(1);

  }

  changePage(value: number): void {

    if (value >= 1 && value <= this.totalPages()) {
      this.page.set(value);
    }

  }

  openDetails(id: number): void {

    if (this.busy()) return;

    this.busy.set(true);
    this.error.set('');
    this.detailError.set('');
    this.message.set('');
    this.integrity.set(null);
    this.history.set([]);
    this.selected.set(null);

    this.medicationService.getMedication(id).subscribe({

      next: record => {

        this.selected.set(record);
        this.busy.set(false);

      },

      error: response => {

        this.error.set(
          this.errorText(
            response,
            'Unable to retrieve blockchain evidence.'
          )
        );

        this.busy.set(false);

      }

    });

  }

  closeDetails(): void {

    if (this.busy()) return;

    this.selected.set(null);
    this.integrity.set(null);
    this.history.set([]);

  }

  verify(): void {

    const record = this.selected();

    if (!record || this.busy()) return;

    this.busy.set(true);
    this.detailError.set('');
    this.integrity.set(null);

    this.medicationService.verifyIntegrity(
      record.medication.id
    ).subscribe({

      next: result => {

        this.integrity.set(result);
        this.busy.set(false);

      },

      error: response => {

        this.detailError.set(
          this.errorText(response, 'Verification request failed.')
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
    this.message.set('');
    this.integrity.set(null);

    this.medicationService.retryAnchor(
      record.medication.id
    ).subscribe({

      next: anchor => {

        this.selected.set({
          medication: record.medication,
          blockchain: anchor
        });

        this.history.set([]);

        this.message.set(
          `Registration status: ${anchor.status}`
        );

        this.busy.set(false);

      },

      error: response => {

        this.detailError.set(
          this.errorText(response, 'Registration retry failed.')
        );

        this.busy.set(false);

      }

    });

  }

  viewHistory(): void {

    const record = this.selected();

    if (!record || this.busy()) return;

    this.busy.set(true);
    this.detailError.set('');

    this.medicationService.getHistory(
      record.medication.id
    ).subscribe({

      next: history => {

        this.history.set(history);
        this.busy.set(false);

      },

      error: response => {

        this.detailError.set(
          this.errorText(response, 'Unable to retrieve history.')
        );

        this.busy.set(false);

      }

    });

  }

  async copy(value: string): Promise<void> {

    try {

      await navigator.clipboard.writeText(value);
      this.message.set('Copied to clipboard.');

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

  openCreateForm(): void {

  if (this.busy() || this.saving()) return;

  this.correctionTarget.set(null);
  this.selected.set(null);
  this.integrity.set(null);
  this.history.set([]);
  this.formError.set('');
  this.notice.set('');

  this.medicationForm.reset({

    patient_id:
      this.patientFilter() ??
      this.patients()[0]?.id ??
      0,

    medication_name: '',
    dosage: '',
    status: 'Pending',

    scheduled_at:
      this.toLocalDateTime(new Date())

  });

  this.formOpen.set(true);

}

openCorrectionForm(): void {

  const record = this.selected();

  if (!record || this.busy() || this.saving()) {
    return;
  }

  this.correctionTarget.set(record.medication);
  this.formError.set('');
  this.notice.set('');

  this.medicationForm.reset({

    patient_id: record.medication.patient_id,

    medication_name:
      record.medication.medication_name,

    dosage: record.medication.dosage,

    status: record.medication.status,

    scheduled_at: this.toLocalDateTime(
      new Date(record.medication.scheduled_at)
    )

  });

  this.selected.set(null);
  this.integrity.set(null);
  this.history.set([]);
  this.formOpen.set(true);

}

closeMedicationForm(): void {

  if (this.saving()) return;

  this.formOpen.set(false);
  this.correctionTarget.set(null);
  this.formError.set('');

}

saveMedication(): void {

  if (this.saving()) return;

  this.formError.set('');

  if (this.medicationForm.invalid) {

    this.medicationForm.markAllAsTouched();

    this.formError.set(
      'Please complete all required fields correctly.'
    );

    return;

  }

  const values = this.medicationForm.getRawValue();

  const scheduledDate = new Date(
    values.scheduled_at
  );

  if (Number.isNaN(scheduledDate.getTime())) {

    this.formError.set(
      'Please enter a valid scheduled date and time.'
    );

    return;

  }

  const target = this.correctionTarget();

  const originalLocalTime = target
    ? this.toLocalDateTime(
        new Date(target.scheduled_at)
      )
    : null;

  const payload: MedicationCorrection = {

    medication_name:
      values.medication_name.trim(),

    dosage: values.dosage.trim(),

    status: values.status,

    scheduled_at:
      target &&
      values.scheduled_at === originalLocalTime
        ? target.scheduled_at
        : scheduledDate.toISOString()

  };

  if (
    payload.medication_name.length < 2 ||
    payload.dosage.length < 1
  ) {

    this.formError.set(
      'Medication name and dosage cannot be empty.'
    );

    return;

  }

  this.saving.set(true);

  const request = target

    ? this.medicationService.correctMedication(
        target.id,
        payload
      )

    : this.medicationService.createMedication({
        patient_id: values.patient_id,
        ...payload
      });

  request.subscribe({

    next: result => {

      this.saving.set(false);
      this.formOpen.set(false);
      this.correctionTarget.set(null);

      this.integrity.set(null);
      this.history.set([]);
      this.detailError.set('');
      this.message.set('');

      const action = target
        ? 'Correction saved'
        : 'Medication record created';

      this.notice.set(
        `${action}. Version ${result.medication.version}. ` +
        `Blockchain registration: ${result.blockchain.status}.`
      );

      this.loadMedications();

      this.selected.set(result);

    },

    error: response => {

      this.saving.set(false);

      this.formError.set(
        this.errorText(
          response,
          'Unable to save medication record.'
        )
      );

    }

  });

}

private toLocalDateTime(date: Date): string {

  const pad = (value: number) =>
    String(value).padStart(2, '0');

  return (
    `${date.getFullYear()}-` +
    `${pad(date.getMonth() + 1)}-` +
    `${pad(date.getDate())}T` +
    `${pad(date.getHours())}:` +
    `${pad(date.getMinutes())}`
  );

}
}