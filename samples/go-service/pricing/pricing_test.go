package pricing

import (
	"errors"
	"testing"
)

func TestTotal(t *testing.T) {
	calc := Calculator{Rules: []Rule{TierDiscount{}, BulkDiscount{MinItems: 10, Percent: 5}}, MaxDiscountPct: 30}
	tests := []struct {
		name  string
		order Order
		want  int64
	}{
		{"gold", Order{10000, "gold", 1}, 9000},
		{"silver", Order{10000, "silver", 1}, 9500},
		{"no tier", Order{10000, "none", 1}, 10000},
		{"bulk at threshold", Order{10000, "none", 10}, 9500},
		{"gold + bulk", Order{10000, "gold", 10}, 8500},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := calc.Total(tt.order)
			if err != nil || got != tt.want {
				t.Fatalf("got %d, %v; want %d", got, err, tt.want)
			}
		})
	}
}

func TestDiscountIsCapped(t *testing.T) {
	calc := Calculator{Rules: []Rule{BulkDiscount{MinItems: 1, Percent: 60}}, MaxDiscountPct: 30}
	if got, _ := calc.Total(Order{10000, "none", 1}); got != 7000 {
		t.Fatalf("got %d, want 7000", got)
	}
}

func TestNegativeSubtotal(t *testing.T) {
	if _, err := (Calculator{}).Total(Order{SubtotalCents: -1}); !errors.Is(err, ErrNegativeSubtotal) {
		t.Fatalf("want ErrNegativeSubtotal, got %v", err)
	}
}
