import { Routes } from '@angular/router';

import { Shell } from './layout/shell/shell';
import { Dashboard } from './pages/dashboard/dashboard';
import { Patients } from './pages/patients/patients';
import { Medications } from './pages/medications/medications';
import { Predictions } from './pages/predictions/predictions';
import { Reports } from './pages/reports/reports';
import { Blockchain } from './pages/blockchain/blockchain';

export const routes: Routes = [
  {
    path: '',
    component: Shell,
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        component: Dashboard,
        title: 'Overview | CareLink'
      },
      {
        path: 'patients',
        component: Patients,
        title: 'Patients | CareLink'
      },
      {
        path: 'medications',
        component: Medications,
        title: 'Medication Records | CareLink'
      },
      {
        path: 'predictions',
        component: Predictions,
        title: 'AI Risk Assessment | CareLink'
      },
      {
        path: 'reports',
        component: Reports,
        title: 'Medical Reports | CareLink'
      },
      {
        path: 'blockchain',
        component: Blockchain,
        title: 'Blockchain Explorer | CareLink'
      }
    ]
  },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];