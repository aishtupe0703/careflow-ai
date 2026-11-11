
from decimal import Decimal


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_million: Decimal,
    output_price_per_million: Decimal,
) -> Decimal:
    """
    Estimate API cost in USD.

    Pricing must be provided per million tokens.
    """
    million = Decimal("1000000")

    input_cost = (
        Decimal(input_tokens)
        / million
        * input_price_per_million
    )

    output_cost = (
        Decimal(output_tokens)
        / million
        * output_price_per_million
    )

    return input_cost + output_cost
