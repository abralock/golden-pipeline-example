import { BulkDiscount, PriceCalculator, TierDiscount, type Order } from "../src/pricing";

const order = (o: Partial<Order> = {}): Order => ({ subtotalCents: 10_000, tier: "none", items: 1, ...o });

describe("PriceCalculator", () => {
  const calc = new PriceCalculator([new TierDiscount(), new BulkDiscount()]);

  it.each([
    ["gold", 9_000],
    ["silver", 9_500],
    ["none", 10_000],
  ] as const)("applies the %s tier discount", (tier, expected) => {
    expect(calc.totalCents(order({ tier }))).toBe(expected);
  });

  it("applies the bulk discount from 10 items", () => {
    expect(calc.totalCents(order({ items: 10 }))).toBe(9_500);
    expect(calc.totalCents(order({ items: 9 }))).toBe(10_000);
  });

  it("caps the total discount", () => {
    const greedy = new PriceCalculator([new BulkDiscount(1, 60)]);
    expect(greedy.totalCents(order())).toBe(7_000);
  });

  it("rejects a negative subtotal", () => {
    expect(() => calc.totalCents(order({ subtotalCents: -1 }))).toThrow(RangeError);
  });
});
