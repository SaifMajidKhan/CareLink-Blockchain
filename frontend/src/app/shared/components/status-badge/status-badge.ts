import {
  Component,
  computed,
  input
} from '@angular/core';

@Component({
  selector: 'app-status-badge',
  templateUrl: './status-badge.html',
  styleUrl: './status-badge.scss'
})
export class StatusBadge {

  readonly status = input.required<string>();

  readonly tone = computed(() => {

    const value = this.status().toLowerCase();

    if ([
      'verified',
      'registered',
      'healthy',
      'online',
      'taken',
      'low'
    ].includes(value)) {
      return 'success';
    }

    if ([
      'pending',
      'medium',
      'not_registered',
      'loading'
    ].includes(value)) {
      return 'warning';
    }

    if ([
      'mismatch',
      'failed',
      'high',
      'missed',
      'unavailable',
      'verification_unavailable',
      'writer_unauthorized'
    ].includes(value)) {
      return 'danger';
    }

    return 'neutral';

  });

  readonly label = computed(() =>
    this.status().replace(/_/g, ' ')
  );

}