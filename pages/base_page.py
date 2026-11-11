from playwright.sync_api import Error as PlaywrightError, Locator, Page

from utils.wait_utils import WaitUtils


class BasePage:
    """
    Base class containing reusable Playwright operations.
    All application Page Objects will inherit this class.
    """

    def __init__(self, page: Page):
        self.page = page

        self.wait = WaitUtils()

    # ================= NAVIGATION =================

    def navigate(self, url: str):
        for attempt in range(3):
            try:
                self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=45000,
                )
                return
            except PlaywrightError as error:
                if (
                    "ERR_NAME_NOT_RESOLVED" not in str(error)
                    or attempt == 2
                ):
                    raise
                delay_ms = 1000 * (attempt + 1)
                print(
                    "CRM hostname lookup failed; retrying navigation "
                    f"in {delay_ms} ms (attempt {attempt + 2}/3)"
                )
                self.page.wait_for_timeout(delay_ms)

    def get_current_url(self):
        return self.page.url

    # ================= ELEMENT ACTIONS =================

    def click(self, locator: Locator):
        self.wait.wait_for_visible(locator)

        locator.click()

    def enter_text(self, locator: Locator, text: str):
        self.wait.wait_for_visible(locator)

        locator.fill(text)
