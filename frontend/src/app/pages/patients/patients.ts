import {
  Component,
  computed,
  inject,
  OnInit,
  signal
} from '@angular/core';

import { DatePipe } from '@angular/common';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import { RouterLink } from '@angular/router';

import {
  LucideAngularModule,
  Users,
  UserPlus,
  Search,
  X,
  RefreshCw,
  ArrowUpRight,
  HeartPulse,
  Activity
} from 'lucide-angular';

import {
  PatientService
} from '../../core/services/patient';

import {
  Patient
} from '../../core/models/patient.models';

import {
  StatCard
} from '../../shared/components/stat-card/stat-card';

@Component({
  selector: 'app-patients',
  imports: [
    DatePipe,
    ReactiveFormsModule,
    RouterLink,
    LucideAngularModule,
    StatCard
  ],
  templateUrl: './patients.html',
  styleUrl: './patients.scss'
})
export class Patients implements OnInit {

  private readonly patientService = inject(PatientService);
  private readonly fb = inject(FormBuilder);

  readonly Users = Users;
  readonly UserPlus = UserPlus;
  readonly Search = Search;
  readonly X = X;
  readonly RefreshCw = RefreshCw;
  readonly ArrowUpRight = ArrowUpRight;
  readonly HeartPulse = HeartPulse;
  readonly Activity = Activity;

  readonly patients = signal<Patient[]>([]);

  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly formOpen = signal(false);

  readonly search = signal('');
  readonly error = signal('');
  readonly formError = signal('');
  readonly success = signal('');

  readonly page = signal(1);
  readonly pageSize = 8;

  readonly patientForm = this.fb.nonNullable.group({

    name: [
      '',
      [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(150)
      ]
    ],

    age: [
      18,
      [
        Validators.required,
        Validators.min(1),
        Validators.max(120),
        Validators.pattern(/^\d+$/)
      ]
    ],

    condition: [
      '',
      [
        Validators.required,
        Validators.minLength(2),
        Validators.maxLength(100)
      ]
    ]

  });

  readonly diabetesCount = computed(() =>
    this.patients().filter(patient =>
      patient.condition.toLowerCase().includes('diabetes')
    ).length
  );

  readonly hypertensionCount = computed(() =>
    this.patients().filter(patient =>
      patient.condition.toLowerCase().includes('hypertension')
    ).length
  );

  readonly filteredPatients = computed(() => {

    const query = this.search().trim().toLowerCase();

    return this.patients().filter(patient =>

      patient.name.toLowerCase().includes(query) ||
      patient.condition.toLowerCase().includes(query) ||
      String(patient.id).includes(query)

    );

  });

  readonly totalPages = computed(() =>
    Math.max(
      1,
      Math.ceil(
        this.filteredPatients().length / this.pageSize
      )
    )
  );

  readonly visiblePatients = computed(() => {

    const start = (this.page() - 1) * this.pageSize;

    return this.filteredPatients().slice(
      start,
      start + this.pageSize
    );

  });

  ngOnInit(): void {
    this.loadPatients();
  }

  loadPatients(): void {

    this.loading.set(true);
    this.error.set('');

    this.patientService.getPatients().subscribe({

      next: patients => {

        this.patients.set(patients);
        this.page.set(1);
        this.loading.set(false);

      },

      error: () => {

        this.error.set(
          'Unable to retrieve patients. Check the backend connection.'
        );

        this.loading.set(false);

      }

    });

  }

  updateSearch(value: string): void {

    this.search.set(value);
    this.page.set(1);

  }

  changePage(page: number): void {

    if (page >= 1 && page <= this.totalPages()) {
      this.page.set(page);
    }

  }

  openForm(): void {

    this.patientForm.reset({
      name: '',
      age: 18,
      condition: ''
    });

    this.formError.set('');
    this.success.set('');
    this.formOpen.set(true);

  }

  closeForm(): void {

    if (!this.saving()) {
      this.formOpen.set(false);
    }

  }

  createPatient(): void {

    if (this.saving()) {
      return;
    }

    if (this.patientForm.invalid) {

      this.patientForm.markAllAsTouched();
      return;

    }

    const values = this.patientForm.getRawValue();

    const payload = {
      name: values.name.trim(),
      age: values.age,
      condition: values.condition.trim()
    };

    if (
      payload.name.length < 2 ||
      payload.condition.length < 2
    ) {

      this.formError.set(
        'Please enter a valid name and condition.'
      );

      return;

    }

    this.saving.set(true);
    this.formError.set('');

    this.patientService.createPatient(payload).subscribe({

      next: patient => {

        this.saving.set(false);
        this.formOpen.set(false);

        this.success.set(
          `${patient.name} registered successfully.`
        );

        this.search.set('');
        this.loadPatients();

      },

      error: response => {

        this.saving.set(false);

        this.formError.set(
          typeof response.error?.detail === 'string'
            ? response.error.detail
            : 'Unable to register patient. Check the entered details.'
        );

      }

    });

  }

  initials(name: string): string {

    return name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map(word => word.charAt(0).toUpperCase())
      .join('');

  }

}