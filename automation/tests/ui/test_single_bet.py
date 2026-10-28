"""TC-01: Verify that an unaffordable bet is rejected without changing
the balance, protecting a critical financial business rule.
"""

import logging
from datetime import date, timedelta

import pytest

from sporty_automation.pages.betting_page import BettingPage
from sporty_automation.test_data import (
    DATE_RANGE_DAYS,
    START_DATE_OFFSET_DAYS,
)
from sporty_automation.util.payout import calculate_payout
from sporty_automation.util.stake import select_stake

pytestmark = pytest.mark.ui
LOGGER = logging.getLogger(__name__)


def test_tc01_single_bet(
    betting_page: BettingPage,
    user_id: str,
) -> None:
    """Protect the core transaction and detect incorrect financial receipt details."""
    start = date.today() + timedelta(days=START_DATE_OFFSET_DAYS)
    end = start + timedelta(days=DATE_RANGE_DAYS)

    betting_page.open(user_id)
    betting_page.wait_until_loaded()
    betting_page.select_date_range(start, end)
    assert betting_page.selected_date_range_label() == (
        f"Date: {start:%d/%m/%Y} \u2014 {end:%d/%m/%Y}"
    )
    betting_page.apply_date_filter()

    displayed_dates = betting_page.displayed_match_dates()
    assert displayed_dates, f"No matches displayed for {start} through {end}"
    for kickoff in displayed_dates:
        assert start <= kickoff <= end, (
            f"Displayed match on {kickoff} is outside {start} through {end}"
        )

    balances_before = betting_page.displayed_balances()
    balance_before = balances_before["header"]
    assert balances_before["bet slip"] == balance_before, (
        f"Balances disagree before placement: {balances_before!r}"
    )
    stake = select_stake(balance_before)
    LOGGER.info(
        "Starting UI balance EUR %s; selected stake EUR %s", balance_before, stake
    )

    selected = betting_page.select_first_home_win()
    slip = betting_page.bet_slip
    assert slip.title() == "Bet Slip"
    assert slip.match_name() == f"{selected.home_team} vs {selected.away_team}"
    assert slip.market() == "Match Winner: Home"
    assert slip.odds() == selected.odds
    assert slip.is_stake_input_enabled(), "Stake input must be visible and enabled"

    slip.enter_stake(str(stake))
    assert slip.stake_value() == str(stake), (
        "Stake input must contain the entered value"
    )
    expected_payout = calculate_payout(stake, selected.odds)
    actual_payout = slip.potential_payout()
    assert actual_payout == expected_payout, (
        f"Expected payout {stake} x {selected.odds} = {expected_payout}, "
        f"but the bet slip displays {actual_payout}"
    )

    receipt = betting_page.receipt
    submitted_at = receipt.browser_time()
    slip.place_bet()
    receipt.wait_until_visible()
    received_at = receipt.browser_time()

    expected = {
        "Bet ID label": "Bet ID",
        "match": f"{selected.home_team} vs {selected.away_team}",
        "stake": stake,
        "odds": selected.odds,
        "payout": expected_payout,
        "selection": "Home",
    }
    actual = {
        "Bet ID label": receipt.bet_id_label(),
        "match": receipt.match_name(),
        "stake": receipt.stake(),
        "odds": receipt.odds(),
        "payout": receipt.potential_payout(),
        "selection": receipt.selection(),
    }
    mismatches = [
        f"Bet receipt — {field}: expected {expected[field]!r}, got {actual[field]!r}"
        for field in expected
        if actual[field] != expected[field]
    ]
    bet_id = receipt.bet_id()
    if not bet_id or not bet_id.lstrip("#").strip():
        mismatches.append(f"Bet ID is missing: {bet_id!r}")
    else:
        LOGGER.info("Receipt Bet ID value is present: %s", bet_id)
    timestamp_error = receipt.timestamp_error(submitted_at, received_at)
    if timestamp_error is not None:
        mismatches.append(timestamp_error)

    receipt.close()
    balance_error = betting_page.balance_update_error(balance_before - stake)
    if balance_error is not None:
        mismatches.append(balance_error)

    if mismatches:
        for mismatch in mismatches:
            LOGGER.error("Single-bet validation failed: %s", mismatch)
        pytest.fail(
            f"{len(mismatches)} failed checks; see ERROR logs above.\n"
            + "\n".join(f"- {mismatch}" for mismatch in mismatches),
            pytrace=False,
        )
