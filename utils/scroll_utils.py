from playwright.sync_api import Page, Locator


class ScrollUtils:

    @staticmethod
    def scroll_to_element(locator: Locator):

        locator.scroll_into_view_if_needed()

    @staticmethod
    def scroll_page_down(page: Page, pixels=500):

        page.evaluate(
            "(pixels) => window.scrollBy(0, pixels)",
            pixels
        )

    @staticmethod
    def scroll_page_up(page: Page, pixels=500):

        page.evaluate(
            "(pixels) => window.scrollBy(0, -pixels)",
            pixels
        )

    @staticmethod
    def scroll_to_bottom(page: Page):

        page.evaluate(
            "() => window.scrollTo(0, document.body.scrollHeight)"
        )

    @staticmethod
    def scroll_to_top(page: Page):

        page.evaluate(
            "() => window.scrollTo(0, 0)"
        )

    @staticmethod
    def scroll_container(
        locator: Locator,
        pixels=500
    ):

        locator.evaluate(
            "(element, pixels) => element.scrollBy(0, pixels)",
            pixels
        )