import {
  Component,
  inject,
  output
} from '@angular/core';

import {
  NavigationEnd,
  Router,
  ActivatedRouteSnapshot
} from '@angular/router';

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

  readonly menuToggle = output<void>();

  readonly Menu = Menu;
  readonly ChevronRight = ChevronRight;
  readonly CalendarDays = CalendarDays;

  readonly currentPage = toSignal(
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      startWith(null),
      map(() => this.getActivePageTitle())
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

  private getActivePageTitle(): string {

    let route: ActivatedRouteSnapshot =
      this.router.routerState.snapshot.root;

    while (route.firstChild) {
      route = route.firstChild;
    }

    return route.title?.split('|')[0].trim() || 'Overview';

  }

}