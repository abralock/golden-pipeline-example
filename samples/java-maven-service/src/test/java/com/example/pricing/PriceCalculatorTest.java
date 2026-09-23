package com.example.pricing;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class PriceCalculatorTest {

    private static final BigDecimal HUNDRED = new BigDecimal("100.00");
    private final PriceCalculator calc = new PriceCalculator(
            List.of(new TierDiscount(), new BulkDiscount(10, new BigDecimal("0.05"))), new BigDecimal("0.30"));

    @ParameterizedTest
    @CsvSource({"GOLD, 90.00", "SILVER, 95.00", "NONE, 100.00"})
    void appliesTierDiscount(Tier tier, String expected) {
        assertEquals(new BigDecimal(expected), calc.total(new Order(HUNDRED, tier, 1)));
    }

    @Test
    void appliesBulkDiscountFromTenItems() {
        assertEquals(new BigDecimal("95.00"), calc.total(new Order(HUNDRED, Tier.NONE, 10)));
        assertEquals(new BigDecimal("100.00"), calc.total(new Order(HUNDRED, Tier.NONE, 9)));
    }

    @Test
    void capsTheTotalDiscount() {
        PriceCalculator greedy = new PriceCalculator(
                List.of(new BulkDiscount(1, new BigDecimal("0.60"))), new BigDecimal("0.30"));
        assertEquals(new BigDecimal("70.00"), greedy.total(new Order(HUNDRED, Tier.NONE, 1)));
    }

    @Test
    void rejectsNegativeSubtotal() {
        assertThrows(IllegalArgumentException.class, () -> new Order(new BigDecimal("-1"), Tier.NONE, 1));
    }
}
