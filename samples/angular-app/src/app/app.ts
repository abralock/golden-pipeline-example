import { ChangeDetectionStrategy, Component } from '@angular/core';

import { PriceTag } from './price-tag/price-tag';
import { PriceCalculator, TierDiscount, type Order } from './pricing/pricing';

@Component({
  selector: 'app-root',
  imports: [PriceTag],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.html',
})
export class App {
  protected readonly order: Order = { subtotalCents: 10_000, tier: 'gold', items: 1 };
  protected readonly totalCents = new PriceCalculator([new TierDiscount()]).totalCents(this.order);
}
