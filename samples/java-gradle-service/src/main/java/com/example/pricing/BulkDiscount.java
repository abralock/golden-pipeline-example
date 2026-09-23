package com.example.pricing;

import java.math.BigDecimal;

/** Percentage off when the order has at least {@code minItems} items. */
public final class BulkDiscount implements DiscountRule {

    private final int minItems;
    private final BigDecimal rate;

    public BulkDiscount(int minItems, BigDecimal rate) {
        this.minItems = minItems;
        this.rate = rate;
    }

    @Override
    public BigDecimal discount(Order order) {
        return order.items() >= minItems ? order.subtotal().multiply(rate) : BigDecimal.ZERO;
    }
}
