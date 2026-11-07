from playwright.sync_api import Browser, Playwright
from utils.config_reader import ConfigReader


class BrowserFactory:

    @staticmethod
    def launch_browser(playwright: Playwright) -> Browser:

        browser_name = ConfigReader.BROWSER.lower()

        browser_type = getattr(playwright, browser_name)

        browser = browser_type.launch(
            headless=ConfigReader.HEADLESS,
            slow_mo=ConfigReader.SLOW_MO,
            args=["--start-maximized"]
        )

        return browser

    @staticmethod
    def create_context(browser: Browser):

        context = browser.new_context(
            no_viewport=True,
            ignore_https_errors=True
        )

        return context