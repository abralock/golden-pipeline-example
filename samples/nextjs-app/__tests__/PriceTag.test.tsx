import { render, screen } from "@testing-library/react";

import { PriceTag } from "@/components/PriceTag";

describe("PriceTag", () => {
  it("shows the original price and the saving when discounted", () => {
    render(<PriceTag originalCents={10_000} finalCents={9_000} />);
    expect(screen.getByLabelText("original price").textContent).toBe("$100.00");
    expect(screen.getByLabelText("price").textContent).toContain("you save $10.00");
  });

  it("shows only the price when there is no discount", () => {
    render(<PriceTag originalCents={10_000} finalCents={10_000} />);
    expect(screen.queryByLabelText("original price")).toBeNull();
    expect(screen.getByLabelText("price").textContent).toContain("$100.00");
  });
});
