from playwright.sync_api import Page


class IframeUtils:

    @staticmethod
    def get_frame_locator(page: Page, iframe_selector: str):

        return page.frame_locator(iframe_selector)

    @staticmethod
    def get_frame_element(
        page: Page,
        iframe_selector: str,
        element_selector: str
    ):

        frame = page.frame_locator(iframe_selector)

        return frame.locator(element_selector)

    @staticmethod
    def fill_frame_element(
        page: Page,
        iframe_selector: str,
        element_selector: str,
        value: str
    ):

        element = IframeUtils.get_frame_element(
            page,
            iframe_selector,
            element_selector
        )

        element.fill(value)

    @staticmethod
    def click_frame_element(
        page: Page,
        iframe_selector: str,
        element_selector: str
    ):

        element = IframeUtils.get_frame_element(
            page,
            iframe_selector,
            element_selector
        )

        element.click()