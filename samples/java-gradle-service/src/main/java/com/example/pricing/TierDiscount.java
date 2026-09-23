package com.example.pricing;

import java.math.BigDecimal;

/** Percentage off by customer tier. */
public final class TierDiscount implements DiscountRule {

    @Override
    public BigDecimal discount(Order order) {
        return order.subtotal().multiply(order.tier().rate());
    }
}
