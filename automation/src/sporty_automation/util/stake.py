"""Select an affordable happy-path stake from the displayed EUR balance."""

from decimal import Decimal

from sporty_automation.test_data import MAX_STAKE, MIN_TEST_STAKE, STAKE_RESERVE


def select_stake(balance: Decimal) -> Decimal:
    if not balance.is_finite() or balance != balance.quantize(Decimal("0.01")):
        raise ValueError(
            f"Expected a finite EUR balance at cent precision, got {balance}"
        )
    stake = min(balance - STAKE_RESERVE, MAX_STAKE)
    if stake < MIN_TEST_STAKE:
        raise ValueError(
            f"Insufficient test funds for TC-01: available EUR {balance}, "
            f"reserve EUR {STAKE_RESERVE}, calculated stake EUR {stake}; "
            f"minimum test stake is EUR {MIN_TEST_STAKE}. No bet submitted."
        )
    return stake.quantize(Decimal("0.01"))
