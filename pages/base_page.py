from playwright.sync_api import Error as PlaywrightError, Locator, Page


class BasePage:
    """Small helper class shared by the page objects."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded")

    def get_current_url(self) -> str:
        return self.page.url

    def click(self, locator: Locator) -> None:
        locator.wait_for(state="visible")
        locator.click()

    def enter_text(self, locator: Locator, text: str) -> None:
        locator.wait_for(state="visible")
        locator.fill(text)

    def wait_for_visible(self, locator: Locator, timeout=15000):
        locator.wait_for(
            state="visible",
            timeout=timeout
        )