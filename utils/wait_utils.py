from playwright.sync_api import Page, Locator


class WaitUtils:

    @staticmethod
    def wait_for_visible(locator: Locator, timeout=15000):

        locator.wait_for(
            state="visible",
            timeout=timeout
        )

    @staticmethod
    def wait_for_hidden(locator: Locator, timeout=15000):

        locator.wait_for(
            state="hidden",
            timeout=timeout
        )

    @staticmethod
    def wait_for_attached(locator: Locator, timeout=15000):

        locator.wait_for(
            state="attached",
            timeout=timeout
        )

    @staticmethod
    def wait_for_url(page: Page, url: str):

        page.wait_for_url(url)

    @staticmethod
    def wait_for_load_state(page: Page):

        page.wait_for_load_state("domcontentloaded")