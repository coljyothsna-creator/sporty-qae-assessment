"""Betting-page navigation, locators, and header readiness check."""

import logging
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from urllib.parse import urlencode

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from sporty_automation.config import Settings
from sporty_automation.pages.components.bet_receipt import BetReceipt
from sporty_automation.pages.components.bet_slip import BetSlip
from sporty_automation.ui.base import BaseUi, Locator

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class HomeSelection:
    home_team: str
    away_team: str
    odds: Decimal


class BettingPage(BaseUi):
    MATCH_LIST_HEADER: Locator = (By.ID, "match-list-header")
    HEADER_BALANCE: Locator = (By.CSS_SELECTOR, "#header-balance > span:last-child")
    SLIP_BALANCE: Locator = (By.ID, "bet-slip-balance")
    DATE_FILTER_TOGGLE: Locator = (By.ID, "date-filter-toggle")
    APPLY_DATE_BUTTON: Locator = (By.ID, "apply-date")
    RESET_BUTTON: Locator = (By.CLASS_NAME, "linkBtn")
    ODDS_FILTER_TOGGLE: Locator = (By.ID, "odds-filter-toggle")
    APPLY_ODDS_BUTTON: Locator = (By.CLASS_NAME, "primaryBtn")
    MATCH_LIST: Locator = (By.CLASS_NAME, "matchList")
    DATE_FILTER_POPOVER: Locator = (By.ID, "date-filter-popover")
    DATE_FILTER_LABEL: Locator = (By.ID, "date-filter-label")
    CALENDAR_MONTH: Locator = (By.ID, "month-label")
    PREVIOUS_MONTH: Locator = (By.ID, "prev-month")
    NEXT_MONTH: Locator = (By.ID, "next-month")
    MATCH_CARDS: Locator = (By.CSS_SELECTOR, ".matchList .matchCard")
    MATCH_DATE_SUFFIX = re.compile(r"-(\d{4}-\d{2}-\d{2})$")
    TEAM_NAMES: Locator = (By.CLASS_NAME, "teamName")
    HOME_ODDS_BUTTON: Locator = (By.CSS_SELECTOR, "button.oddsButton[id$='-home']")
    ODDS_VALUE: Locator = (By.CLASS_NAME, "oddsButtonValue")
    CALENDAR_DAY_XPATH = "//*[@id='calendar-grid']/button[normalize-space(.)='{}']"
    MONTH_NAMES = (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )

    def __init__(self, driver: WebDriver, settings: Settings) -> None:
        super().__init__(driver, settings.ui_timeout)
        self._base_url = settings.base_url
        self.bet_slip = BetSlip(driver, settings.ui_timeout)
        self.receipt = BetReceipt(driver, settings.ui_timeout)

    def open(self, user_id: str) -> None:
        if not user_id.strip():
            raise ValueError("user_id must not be blank")
        LOGGER.info("Opening betting application")
        self.driver.get(f"{self._base_url}/?{urlencode({'user-id': user_id})}")

    def wait_until_loaded(self) -> None:
        LOGGER.info("Waiting for the match-list header to be visible")
        self.visible(self.MATCH_LIST_HEADER)

    def displayed_balances(self) -> dict[str, Decimal]:
        balances = {}
        for name, locator in (
            ("header", self.HEADER_BALANCE),
            ("bet slip", self.SLIP_BALANCE),
        ):
            text = self.visible(locator).text.strip()
            if not text.startswith("Balance: \u20ac"):
                raise ValueError(f"Unexpected {name} balance text: {text!r}")
            balances[name] = Decimal(
                text.removeprefix("Balance: \u20ac").replace(",", "")
            )
        return balances

    def balance_update_error(self, expected: Decimal) -> str | None:
        latest = {}

        def balances_updated(_):
            nonlocal latest
            latest = self.displayed_balances()
            return all(amount == expected for amount in latest.values())

        try:
            WebDriverWait(self.driver, self.timeout).until(balances_updated)
        except TimeoutException:
            return (
                f"Balance did not update within {self.timeout}s after Close: "
                f"expected {expected} in header and bet slip, got {latest!r}"
            )
        LOGGER.info("Header and bet-slip balances updated to %s", expected)
        return None

    def is_date_filter_visible(self) -> bool:
        return self.visible(self.DATE_FILTER_TOGGLE).is_displayed()

    def is_odds_filter_visible(self) -> bool:
        return self.visible(self.ODDS_FILTER_TOGGLE).is_displayed()

    def open_date_filter(self) -> None:
        LOGGER.info("Opening date filter")
        self.click(self.DATE_FILTER_TOGGLE)
        self.visible(self.APPLY_DATE_BUTTON)

    def apply_date_filter(self) -> None:
        LOGGER.info("Applying date filter")
        self.click(self.APPLY_DATE_BUTTON)
        self.wait_until_hidden(self.DATE_FILTER_POPOVER)

    def select_date_range(self, start: date, end: date) -> None:
        if end < start:
            raise ValueError("End date must not precede start date")
        self.open_date_filter()
        self._select_calendar_date(start)
        self._select_calendar_date(end)

    def _select_calendar_date(self, target: date) -> None:
        month_text = self.visible(self.CALENDAR_MONTH).text
        month_name, year = month_text.split()
        current_month = self.MONTH_NAMES.index(month_name) + 1
        offset = (target.year - int(year)) * 12 + target.month - current_month
        direction = self.NEXT_MONTH if offset > 0 else self.PREVIOUS_MONTH
        for _ in range(abs(offset)):
            previous = self.visible(self.CALENDAR_MONTH).text
            self.click(direction)
            WebDriverWait(self.driver, self.timeout).until(
                lambda _, prior=previous: (
                    self.visible(self.CALENDAR_MONTH).text != prior
                )
            )
        self.click((By.XPATH, self.CALENDAR_DAY_XPATH.format(target.day)))

    def selected_date_range_label(self) -> str:
        return self.visible(self.DATE_FILTER_LABEL).text

    def displayed_match_ids(self) -> list[str]:
        self.visible(self.MATCH_LIST)
        WebDriverWait(self.driver, self.timeout).until(
            lambda browser: browser.find_elements(*self.MATCH_CARDS),
            message="No matches available in the selected date range",
        )
        identifiers = []
        for card in self.driver.find_elements(*self.MATCH_CARDS):
            identifier = card.get_dom_attribute("id")
            if identifier is None or not identifier.startswith("match-card-"):
                raise ValueError(f"Unexpected match-card ID: {identifier!r}")
            identifiers.append(identifier.removeprefix("match-card-"))
        return identifiers

    def displayed_match_dates(self) -> list[date]:
        dates = []
        identifiers = self.displayed_match_ids()
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Duplicate match cards displayed")
        for identifier in identifiers:
            suffix = self.MATCH_DATE_SUFFIX.search(identifier)
            if suffix is None:
                raise ValueError(f"Match-card ID has no date suffix: {identifier!r}")
            try:
                kickoff = date.fromisoformat(suffix.group(1))
            except ValueError as error:
                raise ValueError(
                    f"Match-card ID has an invalid date: {identifier!r}"
                ) from error
            LOGGER.info("Filtered match %s has kickoff date %s", identifier, kickoff)
            dates.append(kickoff)
        return dates

    def select_first_home_win(self) -> HomeSelection:
        card = self.visible(self.MATCH_CARDS)
        teams = card.find_elements(*self.TEAM_NAMES)
        if len(teams) != 2:
            raise ValueError(f"Expected two team names on match card, got {len(teams)}")
        button = card.find_element(*self.HOME_ODDS_BUTTON)
        selection = HomeSelection(
            home_team=teams[0].text,
            away_team=teams[1].text,
            odds=Decimal(button.find_element(*self.ODDS_VALUE).text),
        )
        LOGGER.info(
            "Selecting Home Win: %s vs %s", selection.home_team, selection.away_team
        )
        WebDriverWait(self.driver, self.timeout).until(
            lambda _: button.is_displayed() and button.is_enabled()
        )
        button.click()
        return selection
