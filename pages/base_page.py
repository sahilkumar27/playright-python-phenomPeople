from playwright.sync_api import Locator, Page

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
        self.page.goto(url, wait_until="domcontentloaded")

    def get_current_url(self):
        return self.page.url

    # ================= ELEMENT ACTIONS =================

    def click(self, locator: Locator):
        self.wait.wait_for_visible(locator)

        locator.click()

    def enter_text(self, locator: Locator, text: str):
        self.wait.wait_for_visible(locator)

        locator.fill(text)
