namespace Pricing;

/// <summary>Depends on the <see cref="IDiscountRule"/> abstraction, injected via the constructor (DIP).</summary>
/// <param name="rules">Discount rules to apply.</param>
/// <param name="maxDiscountRate">Cap on the total discount, e.g. 0.30 for 30%.</param>
public sealed class PriceCalculator(IEnumerable<IDiscountRule> rules, decimal maxDiscountRate)
{
    private readonly IReadOnlyList<IDiscountRule> _rules = rules.ToList();

    /// <summary>Returns the price after discounts, rounded to cents.</summary>
    public decimal Total(Order order)
    {
        ArgumentNullException.ThrowIfNull(order);
        var discount = _rules.Sum(rule => rule.Discount(order));
        var cap = order.Subtotal * maxDiscountRate;
        return Math.Round(order.Subtotal - Math.Min(discount, cap), 2, MidpointRounding.AwayFromZero);
    }
}
