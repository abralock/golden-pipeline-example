package com.example.pricing;

import java.math.BigDecimal;
import java.util.Objects;

/** Immutable order. Money is BigDecimal, never double. */
public record Order(BigDecimal subtotal, Tier tier, int items) {

    public Order {
        Objects.requireNonNull(subtotal, "subtotal");
        Objects.requireNonNull(tier, "tier");
        if (subtotal.signum() < 0) {
            throw new IllegalArgumentException("subtotal cannot be negative");
        }
    }
}
