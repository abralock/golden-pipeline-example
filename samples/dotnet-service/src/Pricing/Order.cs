namespace Pricing;

/// <summary>Customer tier.</summary>
public enum Tier
{
    /// <summary>No tier discount.</summary>
    None,

    /// <summary>5% off.</summary>
    Silver,

    /// <summary>10% off.</summary>
    Gold,
}

/// <summary>Immutable order. Money is <see cref="decimal"/>, never double.</summary>
public sealed record Order
{
    /// <summary>Creates an order and validates it.</summary>
    public Order(decimal subtotal, Tier tier, int items)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(subtotal);
        Subtotal = subtotal;
        Tier = tier;
        Items = items;
    }

    /// <summary>Order subtotal before discounts.</summary>
    public decimal Subtotal { get; }

    /// <summary>Customer tier.</summary>
    public Tier Tier { get; }

    /// <summary>Number of items.</summary>
    public int Items { get; }
}
