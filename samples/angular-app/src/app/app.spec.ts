import { TestBed } from '@angular/core/testing';

import { App } from './app';

describe('App', () => {
  it('renders the gold member price', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('h1')?.textContent).toBe('Gold member price');
    expect(el.querySelector('strong')?.textContent).toBe('$90.00');
  });
});
