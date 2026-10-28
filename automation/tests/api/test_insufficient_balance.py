"""TC-API-01: Verify that an unaffordable bet is rejected without changing
the balance, protecting a critical financial business rule.
"""

import json
from datetime import date
from decimal import Decimal

import pytest
import requests

from sporty_automation.api.client import BettingApi
from sporty_automation.test_data import MAX_STAKE, MIN_TEST_STAKE
from sporty_automation.util.payout import calculate_payout

SELECTION = "HOME"
STAKE_OVER_BALANCE = Decimal("1.00")
EXPECTED_STATUS = 422
EXPECTED_ERROR = {"error": "insufficient_balance", "message": "Insufficient balance"}


def _json(response: requests.Response, what: str) -> dict:
    try:
        body = response.json()
    except ValueError:
        pytest.fail(
            f"{what}: HTTP {response.status_code}, body is not JSON: "
            f"{response.text[:300]!r}"
        )
    assert isinstance(body, dict), f"{what}: expected JSON object, got {body!r}"
    return body


def _money(value: object, what: str) -> Decimal:
    assert isinstance(value, (int, float)) and not isinstance(value, bool), (
        f"{what}: expected a JSON number, got {value!r}"
    )
    return Decimal(str(value))


def _read_balance(api: BettingApi, label: str) -> Decimal:
    response = api.get_balance()
    assert response.status_code == 200, (
        f"{label} balance: expected HTTP 200, got {response.status_code}: "
        f"{response.text[:300]}"
    )
    body = _json(response, f"{label} balance")
    assert set(body) == {"balance", "currency"}, (
        f"{label} balance: expected keys ['balance', 'currency'], got {sorted(body)}"
    )
    assert body["currency"] == "EUR", (
        f"{label} balance currency: expected 'EUR', got {body['currency']!r}"
    )
    return _money(body["balance"], f"{label} balance")


def _upcoming_match(api: BettingApi) -> dict:
    response = api.get_matches()
    assert response.status_code == 200, f"GET /api/matches: HTTP {response.status_code}"
    today = date.today().isoformat()
    upcoming = [m for m in response.json() if m["kickoffDate"] >= today]
    assert upcoming, "Precondition failed: no upcoming match is available"
    return upcoming[0]


def _success_defects(
    body: dict, match: dict, stake: Decimal, start: Decimal
) -> list[str]:
    """Check an (incorrect) success response against the request and contract."""
    expected_keys = {
        "message", "matchId", "selection", "stake", "odds", "payout",
        "balance", "currency",
    }  # fmt: skip
    defects = []
    if set(body) != expected_keys:
        defects.append(f"keys: expected {sorted(expected_keys)}, got {sorted(body)}")
        return defects
    odds = Decimal(str(match["odds"][SELECTION.lower()]))
    checks = {
        "matchId": (body["matchId"], match["id"]),
        "selection": (body["selection"], SELECTION),
        "stake": (_money(body["stake"], "stake"), stake),
        "odds": (_money(body["odds"], "odds"), odds),
        "payout": (_money(body["payout"], "payout"), calculate_payout(stake, odds)),
        "currency": (body["currency"], "EUR"),
    }
    for field, (actual, expected) in checks.items():
        if actual != expected:
            defects.append(f"{field}: expected {expected!r}, got {actual!r}")
    balance = _money(body["balance"], "balance")
    if balance < 0:
        defects.append(f"balance: negative balance {balance} returned")
    if balance != start:
        defects.append(f"balance: expected unchanged {start}, got {balance}")
    if body["message"] == "Bet placed successfully":
        defects.append("message: success message returned for an unaffordable bet")
    return defects


@pytest.mark.api
def test_tc_api_01_insufficient_balance_rejected(api_client: BettingApi) -> None:
    """A bet above the available balance must be rejected and leave it unchanged.

    Accepting an unaffordable stake would create credit the player never
    deposited and drive the balance negative, so it is a critical financial rule.
    """
    start = _read_balance(api_client, "Initial")
    assert MIN_TEST_STAKE <= start < MAX_STAKE, (
        f"Precondition failed: starting balance {start} must be at least "
        f"{MIN_TEST_STAKE} and below {MAX_STAKE} to perform this negative test; "
        "use --user-id with a suitable "
        "provisioned user. The test does not reset or mutate the account."
    )
    stake = min(MAX_STAKE, start + STAKE_OVER_BALANCE)
    assert start < stake <= MAX_STAKE
    match = _upcoming_match(api_client)

    response = api_client.place_bet(match["id"], SELECTION, float(stake))
    body = _json(response, "place-bet")
    evidence = (
        f"initial balance={start}, stake={stake}, HTTP {response.status_code}, "
        f"body={json.dumps(body)}"
    )
    final = _read_balance(api_client, "Final")

    problems = []
    if response.status_code == 200:
        problems.append("DEFECT: unaffordable bet was accepted with HTTP 200")
        problems += _success_defects(body, match, stake, start)
    else:
        if response.status_code != EXPECTED_STATUS:
            problems.append(
                f"status: expected {EXPECTED_STATUS}, got {response.status_code}"
            )
        if body != EXPECTED_ERROR:
            problems.append(f"body: expected {EXPECTED_ERROR}, got {body}")
    if final != start:
        problems.append(f"final balance: expected {start}, got {final}")

    assert not problems, (
        f"{len(problems)} failed checks; {evidence}, final balance={final}\n- "
        + "\n- ".join(problems)
    )
