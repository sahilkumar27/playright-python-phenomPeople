#
# from playwright.sync_api import Page, expect
#
# from .base_page import BasePage
#
#
# class LoginPage(BasePage):
#     """Represents the Phenom CRM login page."""
#
#     def __init__(self, page: Page):
#
#         super().__init__(page)
#
#         self.username_input = page.locator("#username")
#         self.continue_button = page.locator("#kc-login")
#         self.password_input = page.locator("#phenomPassword3")
#         self.password_login_button = page.locator("input[name='login']")
#         self.error_message = page.locator("[data-test='error']")
#
#     # Navigate to login page
#     def open(self, base_url):
#
#         self.navigate(base_url)
#
#     # Enter credentials and login
#     def login(self, username, password):
#
#         self.enter_text(self.username_input, username)
#         self.click(self.continue_button)
#
#         self.enter_text(self.password_input, password)
#         self.click(self.password_login_button)
#
#     # Verify login error
#     def verify_error(self, message):
#         expect(self.error_message).to_contain_text(message)
#
#     # Verify username field visibility
#     def is_username_visible(self):
#         return self.is_visible(self.username_input)
#
#     # Verify password field visibility
#     def is_password_visible(self):
#         return self.is_visible(self.password_input)
#
#     # Verify login button visibility
#     def is_login_button_visible(self):
#         return self.is_visible(self.continue_button)


from playwright.sync_api import Page

from .base_page import BasePage


class LoginPage(BasePage):
    """Represents the Phenom CRM login page."""

    def __init__(self, page: Page):

        super().__init__(page)

        # Login locators
        self.username_input = page.locator("#username")
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

        self.wait.wait_for_visible(self.password_input)

        self.enter_text(self.password_input, password)

        self.click(self.password_login_button)

    # Complete login flow
    def login(self, username, password):

        self.enter_username(username)

        self.enter_password(password)

