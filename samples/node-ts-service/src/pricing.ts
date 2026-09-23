/**
 * Discount rules. SOLID: one small interface, new behaviour = new class,
 * PriceCalculator depends on the DiscountRule abstraction injected by the caller.
 * Money is integer cents, never floating-point currency.
 */
export interface Order {
  readonly subtotalCents: number;
  readonly tier: "gold" | "silver" | "none";
  readonly items: number;
}

export interface DiscountRule {
  discountCents(order: Order): number;
}

const TIER_PERCENT: Record<Order["tier"], number> = { gold: 10, silver: 5, none: 0 };

export class TierDiscount implements DiscountRule {
  discountCents(order: Order): number {
    return Math.floor((order.subtotalCents * TIER_PERCENT[order.tier]) / 100);
  }
}

export class BulkDiscount implements DiscountRule {
  constructor(
    private readonly minItems = 10,
    private readonly percent = 5,
  ) {}

  discountCents(order: Order): number {
    return order.items >= this.minItems ? Math.floor((order.subtotalCents * this.percent) / 100) : 0;
  }
}

export class PriceCalculator {
  constructor(
    private readonly rules: readonly DiscountRule[],
    private readonly maxDiscountPercent = 30,
  ) {}

  totalCents(order: Order): number {
    if (order.subtotalCents < 0) {
      throw new RangeError("subtotal cannot be negative");
    }
    const discount = this.rules.reduce((sum, rule) => sum + rule.discountCents(order), 0);
    const cap = Math.floor((order.subtotalCents * this.maxDiscountPercent) / 100);
    return order.subtotalCents - Math.min(discount, cap);
  }
}
