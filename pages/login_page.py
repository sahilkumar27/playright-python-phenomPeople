from playwright.sync_api import Page

from .base_page import BasePage


class LoginPage(BasePage):
    """Represents the Phenom CRM login page."""

    def __init__(self, page: Page):

        super().__init__(page)

        # Login locators
        self.username_input = page.locator("#username")
        self.dashboard_search = page.locator("#global-search-input")
        self.continue_button = page.locator("#kc-login")
        self.password_input = page.locator("#phenomPassword3")
        self.password_login_button = page.locator("input[name='login']")

    # Navigate to login page
    def open(self, base_url):

        self.navigate(base_url)

    # Enter username
    def enter_username(self, username):

        self.enter_text(self.username_input, username)

        self.click(self.continue_button)

    # Enter password
    def enter_password(self, password):
        self.enter_text(self.password_input, password)

        self.click(self.password_login_button)

    # Complete login flow
    def login(self, username, password):
        # BASE_URL first loads the CRM host, then redirects either to the
        # login form or to the authenticated dashboard. Wait for the rendered
        # state instead of deciding from the URL, which is shared by both.
        self.page.wait_for_function(
            """() => {
                const visible = selector => {
                    const element = document.querySelector(selector);
                    if (!element) return false;
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' &&
                        style.visibility !== 'hidden' &&
                        element.getClientRects().length > 0;
                };
                return visible('#username') || visible('#global-search-input');
            }""",
            timeout=30000,
        )
        if self.dashboard_search.is_visible():
            print("Already authenticated; CRM dashboard is ready")
            return

        self.enter_username(username)

        self.enter_password(password)
        self.page.wait_for_timeout(7000)


