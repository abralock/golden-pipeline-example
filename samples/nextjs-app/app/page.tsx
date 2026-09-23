import { PriceTag } from "@/components/PriceTag";
import { PriceCalculator, TierDiscount } from "@/lib/pricing";

export default function Home() {
  const order = { subtotalCents: 10_000, tier: "gold", items: 1 } as const;
  const total = new PriceCalculator([new TierDiscount()]).totalCents(order);
  return (
    <main>
      <h1>Gold member price</h1>
      <PriceTag originalCents={order.subtotalCents} finalCents={total} />
    </main>
  );
}
