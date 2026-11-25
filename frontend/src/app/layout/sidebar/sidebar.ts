import { Component, output } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

import {
  LucideAngularModule,
  Activity,
  LayoutDashboard,
  Users,
  Pill,
  BrainCircuit,
  FileText,
  Blocks,
  ShieldCheck
} from 'lucide-angular';

@Component({
  selector: 'app-sidebar',
  imports: [
    RouterLink,
    RouterLinkActive,
    LucideAngularModule
  ],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class Sidebar {

  readonly navigate = output<void>();

  readonly Activity = Activity;
  readonly ShieldCheck = ShieldCheck;

  readonly navigation = [
    {
      label: 'Overview',
      route: '/dashboard',
      icon: LayoutDashboard
    },
    {
      label: 'Patients',
      route: '/patients',
      icon: Users
    },
    {
      label: 'Medication Records',
      route: '/medications',
      icon: Pill
    },
    {
      label: 'AI Risk Assessment',
      route: '/predictions',
      icon: BrainCircuit
    },
    {
      label: 'Medical Reports',
      route: '/reports',
      icon: FileText
    },
    {
      label: 'Blockchain Explorer',
      route: '/blockchain',
      icon: Blocks
    }
  ];
}