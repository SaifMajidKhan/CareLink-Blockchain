import { Component, input } from '@angular/core';

@Component({
  selector: 'app-stat-card',
  templateUrl: './stat-card.html',
  styleUrl: './stat-card.scss'
})
export class StatCard {

  readonly label = input.required<string>();

  readonly value = input.required<string | number>();

  readonly description = input('');

  readonly accent = input('var(--primary)');

}