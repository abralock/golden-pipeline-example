from decimal import Decimal

import pytest

from pricing.discounts import BulkDiscount, CouponDiscount, Order, PriceCalculator, TierDiscount


def order(subtotal="100.00", tier="none", items=1):
    return Order(Decimal(subtotal), tier, items)


@pytest.mark.parametrize("tier,expected", [("gold", "90.00"), ("silver", "95.00"), ("none", "100.00")])
def test_tier_discount(tier, expected):
    assert PriceCalculator([TierDiscount()]).total(order(tier=tier)) == Decimal(expected)


def test_bulk_discount_applies_at_threshold():
    calc = PriceCalculator([BulkDiscount(min_items=10)])
    assert calc.total(order(items=10)) == Decimal("95.00")
    assert calc.total(order(items=9)) == Decimal("100.00")


def test_rules_stack_but_are_capped():
    calc = PriceCalculator([TierDiscount(), BulkDiscount(rate=Decimal("0.50"))])
    assert calc.total(order(tier="gold", items=20)) == Decimal("70.00")  # 60% capped at 30%


def test_negative_subtotal_rejected():
    with pytest.raises(ValueError):
        PriceCalculator([]).total(order(subtotal="-1"))


def test_coupon_discount_known_and_unknown_codes():
    calc = PriceCalculator([CouponDiscount({"SAVE5": Decimal("5")})], max_discount_rate=Decimal("1"))
    assert calc.total(Order(Decimal("100"), "none", 1, coupon="SAVE5")) == Decimal("95.00")
    assert calc.total(Order(Decimal("100"), "none", 1, coupon="BOGUS")) == Decimal("100.00")
    assert calc.total(Order(Decimal("3"), "none", 1, coupon="SAVE5")) == Decimal("0.00")
