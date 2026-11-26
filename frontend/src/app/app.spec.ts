import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { App } from './app';

describe('CareLink Application', () => {

  beforeEach(async () => {

    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideRouter([])
      ]
    }).compileComponents();

  });

  it('should create the CareLink application', () => {

    const fixture = TestBed.createComponent(App);

    expect(fixture.componentInstance).toBeTruthy();

  });

  it('should render the application router outlet', async () => {

    const fixture = TestBed.createComponent(App);

    fixture.detectChanges();

    await fixture.whenStable();

    const compiled = fixture.nativeElement as HTMLElement;

    expect(
      compiled.querySelector('router-outlet')
    ).not.toBeNull();

  });

});