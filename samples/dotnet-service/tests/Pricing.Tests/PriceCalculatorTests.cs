using System.Globalization;

namespace Pricing.Tests;

public class PriceCalculatorTests
{
    private readonly PriceCalculator _calc =
        new([new TierDiscount(), new BulkDiscount(10, 0.05m)], 0.30m);

    [Theory]
    [InlineData(Tier.Gold, "90.00")]
    [InlineData(Tier.Silver, "95.00")]
    [InlineData(Tier.None, "100.00")]
    public void AppliesTierDiscount(Tier tier, string expected)
    {
        Assert.Equal(decimal.Parse(expected, CultureInfo.InvariantCulture), _calc.Total(new Order(100m, tier, 1)));
    }

    [Fact]
    public void AppliesBulkDiscountFromTenItems()
    {
        Assert.Equal(95.00m, _calc.Total(new Order(100m, Tier.None, 10)));
        Assert.Equal(100.00m, _calc.Total(new Order(100m, Tier.None, 9)));
    }

    [Fact]
    public void CapsTheTotalDiscount()
    {
        var greedy = new PriceCalculator([new BulkDiscount(1, 0.60m)], 0.30m);
        Assert.Equal(70.00m, greedy.Total(new Order(100m, Tier.None, 1)));
    }

    [Fact]
    public void RejectsNegativeSubtotal()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new Order(-1m, Tier.None, 1));
    }
}
