"""Discount rules. Example of SOLID-friendly design the architecture tests / reviewers look for:

- S: each rule has one reason to change.
- O: add a new rule by adding a class, not by editing PriceCalculator.
- L: every DiscountRule is interchangeable.
- I: the rule interface is one method.
- D: PriceCalculator depends on the DiscountRule abstraction, injected by the caller.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class Order:
    subtotal: Decimal
    customer_tier: str
    item_count: int
    coupon: str | None = None


class DiscountRule(ABC):
    @abstractmethod
    def discount(self, order: Order) -> Decimal:
        """Return the discount amount (not percentage) for this order."""


class TierDiscount(DiscountRule):
    RATES = {"gold": Decimal("0.10"), "silver": Decimal("0.05")}

    def discount(self, order: Order) -> Decimal:
        return order.subtotal * self.RATES.get(order.customer_tier, Decimal("0"))


class BulkDiscount(DiscountRule):
    def __init__(self, min_items: int = 10, rate: Decimal = Decimal("0.05")) -> None:
        self._min_items = min_items
        self._rate = rate

    def discount(self, order: Order) -> Decimal:
        return order.subtotal * self._rate if order.item_count >= self._min_items else Decimal("0")


class PriceCalculator:
    def __init__(self, rules: Iterable[DiscountRule], max_discount_rate: Decimal = Decimal("0.30")) -> None:
        self._rules = list(rules)
        self._max_rate = max_discount_rate

    def total(self, order: Order) -> Decimal:
        if order.subtotal < 0:
            raise ValueError("subtotal cannot be negative")
        discount = sum((r.discount(order) for r in self._rules), Decimal("0"))
        discount = min(discount, order.subtotal * self._max_rate)
        return (order.subtotal - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class CouponDiscount(DiscountRule):
    def __init__(self, codes: dict[str, Decimal]) -> None:
        self._codes = codes

    def discount(self, order: Order) -> Decimal:
        amount = self._codes.get(order.coupon or "", Decimal("0"))
        return min(amount, order.subtotal)
