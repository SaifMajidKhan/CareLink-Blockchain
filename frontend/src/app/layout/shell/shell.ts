import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { Sidebar } from '../sidebar/sidebar';
import { Header } from '../header/header';

@Component({
  selector: 'app-shell',
  imports: [
    RouterOutlet,
    Sidebar,
    Header
  ],
  templateUrl: './shell.html',
  styleUrl: './shell.scss'
})
export class Shell {

  readonly mobileMenuOpen = signal(false);

  toggleMenu(): void {
    this.mobileMenuOpen.update(value => !value);
  }

  closeMenu(): void {
    this.mobileMenuOpen.set(false);
  }

}