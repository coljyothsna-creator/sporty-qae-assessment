"""pytest lifecycle, runtime options, and failure evidence."""

import logging
import re
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from sporty_automation.api.client import BettingApi
from sporty_automation.config import DEFAULT_BASE_URL, Settings
from sporty_automation.pages.betting_page import BettingPage

LOGGER = logging.getLogger(__name__)
ARTIFACTS = Path(__file__).resolve().parent / "artifacts"


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("sporty")
    group.addoption("--base-url", default=DEFAULT_BASE_URL)
    group.addoption("--ui-timeout", type=float, default=10)
    group.addoption("--api-timeout", type=float, default=10)
    group.addoption("--headed", action="store_true", help="Show the Chrome window")
    group.addoption(
        "--user-id",
        default=None,
        help="Use a supplied user context instead of generating an isolated user",
    )


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    return Settings(
        base_url=pytestconfig.getoption("--base-url"),
        ui_timeout=pytestconfig.getoption("--ui-timeout"),
        api_timeout=pytestconfig.getoption("--api-timeout"),
        headless=not pytestconfig.getoption("--headed"),
    )


@pytest.fixture
def user_id(pytestconfig: pytest.Config) -> str:
    supplied = pytestconfig.getoption("--user-id")
    if supplied is None:
        return f"assessment-{uuid4().hex}"
    if not supplied.strip():
        raise pytest.UsageError("--user-id must not be blank")
    return supplied


@pytest.fixture
def driver(settings: Settings) -> Iterator[WebDriver]:
    options = Options()
    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")
    LOGGER.info("Starting Chrome")
    browser = webdriver.Chrome(options=options)
    try:
        browser.set_page_load_timeout(settings.ui_timeout)
        yield browser
    finally:
        LOGGER.info("Closing Chrome")
        browser.quit()


@pytest.fixture
def api_client(settings: Settings, user_id: str) -> Iterator[BettingApi]:
    with requests.Session() as session:
        yield BettingApi(session, settings, user_id)


@pytest.fixture
def betting_page(driver: WebDriver, settings: Settings) -> BettingPage:
    return BettingPage(driver, settings)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if not report.failed or report.when not in {"setup", "call"}:
        return
    browser = item.funcargs.get("driver")
    if browser is None:
        return
    filename = re.sub(r"[^A-Za-z0-9_.-]", "_", item.nodeid)[:100]
    screenshot = ARTIFACTS / "screenshots" / f"{filename}-{uuid4().hex}.png"
    try:
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        if not browser.save_screenshot(str(screenshot)):
            raise OSError("WebDriver did not save the screenshot")
    except (OSError, WebDriverException):
        LOGGER.exception("Could not capture failure screenshot")
        report.sections.append(("Screenshot", "Capture failed; see logs"))
    else:
        LOGGER.error("Failure screenshot: %s", screenshot)
        report.sections.append(("Screenshot", str(screenshot)))
