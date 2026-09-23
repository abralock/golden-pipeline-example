// Command pricing prints a sample price. Keep main thin: logic lives in run() so it is testable.
package main

import (
	"fmt"
	"io"
	"os"

	"example.com/pricing-service/pricing"
)

func run(w io.Writer, subtotalCents int64) error {
	calc := pricing.Calculator{Rules: []pricing.Rule{pricing.TierDiscount{}}, MaxDiscountPct: 30}
	total, err := calc.Total(pricing.Order{SubtotalCents: subtotalCents, Tier: "gold", Items: 1})
	if err != nil {
		return fmt.Errorf("pricing: %w", err)
	}
	_, err = fmt.Fprintf(w, "total: %d cents\n", total)
	return err
}

func main() {
	if err := run(os.Stdout, 10000); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
