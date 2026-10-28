"""Expected EUR payout rounded to cents, with exact halfway values rounded down."""

from decimal import ROUND_HALF_DOWN, Decimal


def calculate_payout(stake: Decimal, odds: Decimal) -> Decimal:
    return (stake * odds).quantize(Decimal("0.01"), rounding=ROUND_HALF_DOWN)
