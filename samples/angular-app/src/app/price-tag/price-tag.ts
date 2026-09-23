import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { formatCents } from '../pricing/pricing';

@Component({
  selector: 'app-price-tag',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p aria-label="price">
      @if (discounted()) {
        <s aria-label="original price">{{ original() }}</s>
      }
      <strong>{{ final() }}</strong>
      @if (discounted()) {
        <span> (you save {{ saving() }})</span>
      }
    </p>
  `,
})
export class PriceTag {
  readonly originalCents = input.required<number>();
  readonly finalCents = input.required<number>();

  protected readonly discounted = computed(() => this.finalCents() < this.originalCents());
  protected readonly original = computed(() => formatCents(this.originalCents()));
  protected readonly final = computed(() => formatCents(this.finalCents()));
  protected readonly saving = computed(() => formatCents(this.originalCents() - this.finalCents()));
}
