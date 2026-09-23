import { TestBed } from '@angular/core/testing';

import { PriceTag } from './price-tag';

function render(originalCents: number, finalCents: number): HTMLElement {
  const fixture = TestBed.createComponent(PriceTag);
  fixture.componentRef.setInput('originalCents', originalCents);
  fixture.componentRef.setInput('finalCents', finalCents);
  fixture.detectChanges();
  return fixture.nativeElement as HTMLElement;
}

describe('PriceTag', () => {
  it('shows the original price and the saving when discounted', () => {
    const el = render(10_000, 9_000);
    expect(el.querySelector('[aria-label="original price"]')?.textContent).toBe('$100.00');
    expect(el.querySelector('[aria-label="price"]')?.textContent).toContain('you save $10.00');
  });

  it('shows only the price when there is no discount', () => {
    const el = render(10_000, 10_000);
    expect(el.querySelector('[aria-label="original price"]')).toBeNull();
    expect(el.querySelector('strong')?.textContent).toBe('$100.00');
  });
});
