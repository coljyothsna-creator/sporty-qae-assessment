"""Bet-slip interactions and reads; expected values remain in the test."""

import logging
from decimal import Decimal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from sporty_automation.ui.base import BaseUi, Locator

LOGGER = logging.getLogger(__name__)


class BetSlip(BaseUi):
    ROOT: Locator = (By.ID, "bet-slip")
    TITLE: Locator = (By.ID, "bet-slip-title")
    MATCH_NAME: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionTeams")
    MARKET: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionMarket")
    ODDS: Locator = (By.CSS_SELECTOR, "#bet-slip .betSelectionOdds")
    STAKE_INPUT: Locator = (By.ID, "bet-slip-stake-input")
    POTENTIAL_PAYOUT: Locator = (By.ID, "bet-slip-potential-payout")
    PLACE_BET: Locator = (By.ID, "bet-slip-place-bet")

    def title(self) -> str:
        return self.visible(self.TITLE).text

    def match_name(self) -> str:
        return self.visible(self.MATCH_NAME).text

    def market(self) -> str:
        return self.visible(self.MARKET).text

    def odds(self) -> Decimal:
        text = self.visible(self.ODDS).text
        if not text.startswith("Odds: "):
            raise ValueError(f"Unexpected bet-slip odds text: {text!r}")
        return Decimal(text.removeprefix("Odds: "))

    def is_stake_input_enabled(self) -> bool:
        return self.visible(self.STAKE_INPUT).is_enabled()

    def enter_stake(self, value: str) -> None:
        self.fill(self.STAKE_INPUT, value)

    def stake_value(self) -> str:
        return self.visible(self.STAKE_INPUT).get_property("value")

    def potential_payout(self) -> Decimal:
        text = self.visible(self.POTENTIAL_PAYOUT).text
        if not text.startswith("\u20ac"):
            raise ValueError(f"Expected EUR potential payout, got {text!r}")
        return Decimal(text.removeprefix("\u20ac").replace(",", ""))

    def place_bet(self) -> None:
        try:
            self.click(self.PLACE_BET)
        except TimeoutException as error:
            buttons = self.driver.find_elements(*self.PLACE_BET)
            if not buttons:
                state = "not found in the DOM"
            else:
                button = buttons[0]
                state = (
                    f"present, visible={button.is_displayed()}, "
                    f"enabled={button.is_enabled()}"
                )
            roots = self.driver.find_elements(*self.ROOT)
            feedback = "\n".join(root.text for root in roots if root.is_displayed())
            message = (
                f"Place Bet did not become clickable within {self.timeout}s: {state}. "
                "No bet was submitted by this action. "
                f"Visible bet-slip details:\n{feedback or '(no visible bet slip)'}"
            )
            LOGGER.error(message)
            raise TimeoutException(message) from error
