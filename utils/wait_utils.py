from playwright.sync_api import Locator


class WaitUtils:

    @staticmethod
    def wait_for_visible(locator: Locator, timeout=15000):

        locator.wait_for(
            state="visible",
            timeout=timeout
        )
