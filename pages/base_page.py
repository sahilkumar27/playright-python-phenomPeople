from playwright.sync_api import Locator, Page, TimeoutError

from utils.wait_utils import WaitUtils
from utils.scroll_utils import ScrollUtils
from utils.window_utils import WindowUtils
from utils.iframe_utils import IframeUtils


class BasePage:
    """
    Base class containing reusable Playwright operations.
    All application Page Objects will inherit this class.
    """

    def __init__(self, page: Page):
        self.page = page

        # Initialize reusable utility classes
        self.wait = WaitUtils()
        self.scroll = ScrollUtils()
        self.window = WindowUtils()
        self.iframe = IframeUtils()

    # ================= NAVIGATION =================

    def navigate(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded")

    def refresh_page(self):
        self.page.reload(wait_until="domcontentloaded")

    def get_current_url(self):
        return self.page.url

    def get_page_title(self):
        return self.page.title()

    # ================= ELEMENT ACTIONS =================

    def click(self, locator: Locator):
        self.wait.wait_for_visible(locator)

        locator.click()

    def double_click(self, locator: Locator):
        self.wait.wait_for_visible(locator)

        locator.dblclick()

    def enter_text(self, locator: Locator, text: str):
        self.wait.wait_for_visible(locator)

        locator.fill(text)

    def clear_text(self, locator: Locator):
        self.wait.wait_for_visible(locator)

        locator.clear()

    def get_text(self, locator: Locator):
        self.wait.wait_for_visible(locator)

        return locator.inner_text()

    def is_visible(self, locator: Locator):
        try:
            locator.wait_for(state="visible")
            return True
        except TimeoutError:
            return False

    def is_enabled(self, locator: Locator):
        return locator.is_enabled()

    def wait_for_element(self, locator: Locator):
        self.wait.wait_for_visible(locator)

    # ================= DROPDOWN =================

    def select_dropdown_option(
            self,
            locator: Locator,
            value: str
    ):
        self.wait.wait_for_visible(locator)

        locator.select_option(value)

    # ================= CHECKBOX =================

    def check_checkbox(self, locator: Locator):
        self.wait.wait_for_visible(locator)

        locator.check()

    def uncheck_checkbox(self, locator: Locator):
        self.wait.wait_for_visible(locator)

        locator.uncheck()

    # ================= SCROLL =================

    def scroll_to_element(self, locator: Locator):
        self.scroll.scroll_to_element(locator)

    def scroll_vertical(self, pixels: int):
        self.scroll.scroll_page_down(self.page, pixels)

    def scroll_to_bottom(self):
        self.scroll.scroll_to_bottom(self.page)

    def scroll_to_top(self):
        self.scroll.scroll_to_top(self.page)

    # ================= WINDOW / TAB =================

    def get_all_tabs(self):
        return self.window.get_all_pages(self.page)

    # ================= IFRAME =================

    def get_iframe(self, iframe_selector: str):
        return self.iframe.get_frame_locator(
            self.page,
            iframe_selector
        )

    # ================= PAGE LOAD =================

    def wait_for_page_load(self):
        self.wait.wait_for_load_state(self.page)
