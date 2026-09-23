/**
 * Business logic stays out of components so it is unit-testable.
 * SOLID: small interface, new behaviour = new class, calculator depends on the abstraction.
 * Money is integer cents.
 */
export type Tier = 'gold' | 'silver' | 'none';

export interface Order {
  readonly subtotalCents: number;
  readonly tier: Tier;
  readonly items: number;
}

export interface DiscountRule {
  discountCents(order: Order): number;
}

const TIER_PERCENT: Record<Tier, number> = { gold: 10, silver: 5, none: 0 };

export class TierDiscount implements DiscountRule {
  discountCents(order: Order): number {
    return Math.floor((order.subtotalCents * TIER_PERCENT[order.tier]) / 100);
  }
}

export class PriceCalculator {
  constructor(
    private readonly rules: readonly DiscountRule[],
    private readonly maxDiscountPercent = 30,
  ) {}

  totalCents(order: Order): number {
    if (order.subtotalCents < 0) {
      throw new RangeError('subtotal cannot be negative');
    }
    const discount = this.rules.reduce((sum, rule) => sum + rule.discountCents(order), 0);
    const cap = Math.floor((order.subtotalCents * this.maxDiscountPercent) / 100);
    return order.subtotalCents - Math.min(discount, cap);
  }
}

export function formatCents(cents: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(cents / 100);
}
