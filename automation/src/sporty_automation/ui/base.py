"""Only common interactions that add synchronization beyond Selenium."""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class BaseUi:
    def __init__(self, driver: WebDriver, timeout: float) -> None:
        self.driver = driver
        self.timeout = timeout

    def visible(self, locator: Locator) -> WebElement:
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def click(self, locator: Locator) -> None:
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator),
            message=(
                f"Element {locator!r} did not become visible and enabled "
                f"within {self.timeout}s"
            ),
        )
        element.click()

    def fill(self, locator: Locator, value: str) -> None:
        element = self.visible(locator)
        element.clear()
        element.send_keys(value)

    def wait_until_hidden(self, locator: Locator) -> None:
        WebDriverWait(self.driver, self.timeout).until(
            EC.invisibility_of_element_located(locator)
        )

    def scroll_into_view(self, locator: Locator) -> None:
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
