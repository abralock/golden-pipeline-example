package com.example.pricing;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

/** Depends on the DiscountRule abstraction, injected through the constructor (DIP). */
public final class PriceCalculator {

    private final List<DiscountRule> rules;
    private final BigDecimal maxDiscountRate;

    public PriceCalculator(List<DiscountRule> rules, BigDecimal maxDiscountRate) {
        this.rules = List.copyOf(rules);
        this.maxDiscountRate = maxDiscountRate;
    }

    public BigDecimal total(Order order) {
        BigDecimal discount = rules.stream()
                .map(rule -> rule.discount(order))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal cap = order.subtotal().multiply(maxDiscountRate);
        return order.subtotal().subtract(discount.min(cap)).setScale(2, RoundingMode.HALF_UP);
    }
}
