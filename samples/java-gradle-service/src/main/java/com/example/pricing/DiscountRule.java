package com.example.pricing;

import java.math.BigDecimal;

/** One small abstraction (ISP). Add behaviour by adding a rule class (OCP), not by editing PriceCalculator. */
public interface DiscountRule {

    /** Returns the discount amount (not a percentage) for the order. */
    BigDecimal discount(Order order);
}
