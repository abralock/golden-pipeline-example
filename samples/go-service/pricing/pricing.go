// Package pricing applies discount rules to orders.
//
// SOLID in Go terms: small interface (Rule), new behaviour = new type,
// Calculator depends on the Rule abstraction injected by the caller.
// Money is int64 cents, never float64.
package pricing

import "errors"

// Order is an immutable order value.
type Order struct {
	SubtotalCents int64
	Tier          string
	Items         int
}

// Rule returns the discount in cents for an order.
type Rule interface {
	Discount(o Order) int64
}

// TierDiscount gives a percentage off per customer tier.
type TierDiscount struct{}

var tierPercent = map[string]int64{"gold": 10, "silver": 5}

// Discount implements Rule.
func (TierDiscount) Discount(o Order) int64 {
	return o.SubtotalCents * tierPercent[o.Tier] / 100
}

// BulkDiscount gives Percent off when Items >= MinItems.
type BulkDiscount struct {
	MinItems int
	Percent  int64
}

// Discount implements Rule.
func (b BulkDiscount) Discount(o Order) int64 {
	if o.Items < b.MinItems {
		return 0
	}
	return o.SubtotalCents * b.Percent / 100
}

// ErrNegativeSubtotal is returned for invalid orders.
var ErrNegativeSubtotal = errors.New("subtotal cannot be negative")

// Calculator sums rules and caps the total discount.
type Calculator struct {
	Rules          []Rule
	MaxDiscountPct int64
}

// Total returns the price after discounts, in cents.
func (c Calculator) Total(o Order) (int64, error) {
	if o.SubtotalCents < 0 {
		return 0, ErrNegativeSubtotal
	}
	var discount int64
	for _, r := range c.Rules {
		discount += r.Discount(o)
	}
	maxDiscount := o.SubtotalCents * c.MaxDiscountPct / 100
	return o.SubtotalCents - min(discount, maxDiscount), nil
}
