import {
  Component,
  inject,
  output
} from '@angular/core';

import { Title } from '@angular/platform-browser';
import { NavigationEnd, Router } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';

import {
  filter,
  map,
  startWith
} from 'rxjs';

import {
  LucideAngularModule,
  Menu,
  ChevronRight,
  CalendarDays
} from 'lucide-angular';

@Component({
  selector: 'app-header',
  imports: [LucideAngularModule],
  templateUrl: './header.html',
  styleUrl: './header.scss'
})
export class Header {

  private readonly router = inject(Router);
  private readonly title = inject(Title);

  readonly menuToggle = output<void>();

  readonly Menu = Menu;
  readonly ChevronRight = ChevronRight;
  readonly CalendarDays = CalendarDays;

  readonly currentPage = toSignal(
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      startWith(null),
      map(() =>
        this.title.getTitle().split(' | ')[0]
      )
    ),
    { initialValue: 'Overview' }
  );

  readonly today = new Intl.DateTimeFormat(
    'en-GB',
    {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }
  ).format(new Date());

}