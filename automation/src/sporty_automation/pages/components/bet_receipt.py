"""Receipt reads and a terminal placement wait, without submission retries."""

import logging
from datetime import datetime
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from sporty_automation.ui.base import BaseUi, Locator
from sporty_automation.util.receipt_timestamp import (
    browser_local_time,
    receipt_timestamp_error,
)

LOGGER = logging.getLogger(__name__)


class BetReceipt(BaseUi):
    SUCCESS: Locator = (By.ID, "modal-success")
    ERROR: Locator = (
        By.XPATH,
        "//*[@role='dialog'][.//*[normalize-space(.)='Something went wrong']]",
    )
    BET_ID: Locator = (By.ID, "modal-success-bet-id")
    BET_ID_LABEL: Locator = (
        By.XPATH,
        "//*[@id='modal-success-bet-id']/preceding-sibling::span",
    )
    MATCH: Locator = (By.ID, "modal-success-match")
    STAKE: Locator = (By.ID, "modal-success-stake")
    ODDS: Locator = (By.ID, "modal-success-odds")
    PAYOUT: Locator = (By.ID, "modal-success-payout")
    PLACED_AT: Locator = (By.ID, "modal-success-placed-at")
    CLOSE: Locator = (By.ID, "modal-success-close")
    SELECTION: Locator = (
        By.XPATH,
        "//*[@id='modal-success']"
        "//*[contains(concat(' ',normalize-space(@class),' '),' modalMicroLabel ')"
        " and (normalize-space(.)='Selection' or normalize-space(.)='Match Winner')]"
        "/following-sibling::*[1]",
    )

    def wait_until_visible(self) -> None:
        def terminal_result(_):
            errors = self.driver.find_elements(*self.ERROR)
            for error in errors:
                if error.is_displayed():
                    raise AssertionError(f"Bet placement failed: {error.text}")
            return any(
                element.is_displayed()
                for element in self.driver.find_elements(*self.SUCCESS)
            )

        WebDriverWait(self.driver, self.timeout).until(
            terminal_result, message="Bet placement did not produce a receipt or error"
        )

    def bet_id(self) -> str:
        return self.visible(self.BET_ID).text.strip()

    def close(self) -> None:
        self.click(self.CLOSE)
        self.wait_until_hidden(self.SUCCESS)

    def bet_id_label(self) -> str:
        return self.visible(self.BET_ID_LABEL).text.strip()

    def match_name(self) -> str:
        return self.visible(self.MATCH).text

    def stake(self) -> Decimal:
        return self._eur_amount(self.STAKE)

    def odds(self) -> Decimal:
        return Decimal(self.visible(self.ODDS).text)

    def potential_payout(self) -> Decimal:
        return self._eur_amount(self.PAYOUT)

    def placed_at(self) -> str:
        return self.visible(self.PLACED_AT).text

    def browser_time(self) -> datetime:
        return browser_local_time(self.driver)

    def timestamp_error(
        self, submitted_at: datetime, received_at: datetime
    ) -> str | None:
        text = self.placed_at()
        error = receipt_timestamp_error(text, submitted_at, received_at)
        if error is None:
            LOGGER.info(
                "Receipt timestamp is within browser submission window: %s", text
            )
        return error

    def selection(self) -> str | None:
        """Return no value when the receipt omits its labeled selection field."""
        for element in self.driver.find_elements(*self.SELECTION):
            if element.is_displayed():
                return element.text.strip()
        return None

    def _eur_amount(self, locator: Locator) -> Decimal:
        text = self.visible(locator).text
        if not text.startswith("\u20ac"):
            raise ValueError(f"Expected EUR receipt amount, got {text!r}")
        return Decimal(text.removeprefix("\u20ac").replace(",", ""))
