namespace Pricing;

/// <summary>One small abstraction (ISP). Add behaviour with a new rule class (OCP).</summary>
public interface IDiscountRule
{
    /// <summary>Returns the discount amount (not a percentage) for the order.</summary>
    decimal Discount(Order order);
}

/// <summary>Percentage off by customer tier.</summary>
public sealed class TierDiscount : IDiscountRule
{
    /// <inheritdoc />
    public decimal Discount(Order order) => order.Subtotal * order.Tier switch
    {
        Tier.Gold => 0.10m,
        Tier.Silver => 0.05m,
        _ => 0m,
    };
}

/// <summary>Percentage off when the order has at least <paramref name="minItems"/> items.</summary>
/// <param name="minItems">Minimum number of items.</param>
/// <param name="rate">Discount rate, e.g. 0.05 for 5%.</param>
public sealed class BulkDiscount(int minItems, decimal rate) : IDiscountRule
{
    /// <inheritdoc />
    public decimal Discount(Order order) => order.Items >= minItems ? order.Subtotal * rate : 0m;
}
