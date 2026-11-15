
from playwright.sync_api import Page, expect

from .base_page import BasePage


class LoginPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

        self.username_input = page.locator("#username")
        self.continue_button = page.locator("#kc-login")
        self.password_input = page.locator("#phenomPassword3")
        self.login_button = page.locator("input[name='login']")
        self.dashboard_search = page.locator("#global-search-input")

    def open(self, base_url: str):
        self.page.goto(base_url, wait_until="domcontentloaded")

    def enter_email(self, username: str):
        self.username_input.wait_for(state="visible")
        self.username_input.fill(username)
        self.continue_button.click()

    def enter_password(self, password: str):
        self.password_input.wait_for(state="visible")
        self.password_input.fill(password)

    def login(self, username: str, password: str):
        self.enter_email(username)
        self.enter_password(password)
        self.login_button.click()

        # Verify dashboard is displayed
        expect(self.dashboard_search).to_be_visible(
            timeout=30000
        )
