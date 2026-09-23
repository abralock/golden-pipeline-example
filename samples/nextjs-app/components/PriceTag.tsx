import { formatCents } from "@/lib/pricing";

interface Props {
  readonly originalCents: number;
  readonly finalCents: number;
}

export function PriceTag({ originalCents, finalCents }: Props) {
  const discounted = finalCents < originalCents;
  return (
    <p aria-label="price">
      {discounted && <s aria-label="original price">{formatCents(originalCents)}</s>}{" "}
      <strong>{formatCents(finalCents)}</strong>
      {discounted && <span> (you save {formatCents(originalCents - finalCents)})</span>}
    </p>
  );
}
