package com.example.pricing;

import java.math.BigDecimal;

/** Customer tier with its discount rate. */
public enum Tier {
    GOLD(new BigDecimal("0.10")),
    SILVER(new BigDecimal("0.05")),
    NONE(BigDecimal.ZERO);

    private final BigDecimal rate;

    Tier(BigDecimal rate) {
        this.rate = rate;
    }

    public BigDecimal rate() {
        return rate;
    }
}
