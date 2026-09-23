import { formatCents, PriceCalculator, TierDiscount, type Order } from "@/lib/pricing";

const order = (o: Partial<Order> = {}): Order => ({ subtotalCents: 10_000, tier: "none", items: 1, ...o });

describe("PriceCalculator", () => {
  const calc = new PriceCalculator([new TierDiscount()]);

  it.each([
    ["gold", 9_000],
    ["silver", 9_500],
    ["none", 10_000],
  ] as const)("applies the %s tier discount", (tier, expected) => {
    expect(calc.totalCents(order({ tier }))).toBe(expected);
  });

  it("caps the discount", () => {
    const capped = new PriceCalculator([new TierDiscount()], 5);
    expect(capped.totalCents(order({ tier: "gold" }))).toBe(9_500);
  });

  it("rejects a negative subtotal", () => {
    expect(() => calc.totalCents(order({ subtotalCents: -1 }))).toThrow(RangeError);
  });
});

describe("formatCents", () => {
  it("formats cents as currency", () => {
    expect(formatCents(123_456)).toBe("$1,234.56");
  });
});
