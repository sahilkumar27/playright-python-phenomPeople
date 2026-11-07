# import pytest
#
# from utils.config_reader import ConfigReader
#
#
# @pytest.mark.smoke
# class TestPhenomLogin:
#
#     def test_valid_login(self, login_page):
#
#         # Step 1: Open Phenom application
#         login_page.open(ConfigReader.BASE_URL)
#
#         print("Phenom application opened successfully")
#
#         # Step 2: Verify login page elements
#         assert login_page.is_username_visible(), \
#             "Username field is not visible"
#
#         assert login_page.is_login_button_visible(), \
#             "Login button is not visible"
#
#         print("Login page elements verified successfully")
#
#         # Step 3: Enter valid credentials
#         login_page.login(
#             ConfigReader.USERNAME,
#             ConfigReader.PASSWORD
#         )
#
#         print("Login credentials submitted successfully")
#
#         # Step 4: Verify successful navigation
#         login_page.page.wait_for_url(
#             lambda url: url.startswith(
#                 "https://uat-pipeline.phenompeople.com"
#             ),
#             timeout=30000
#         )
#
#         print("Login successful")
#         print("Current URL:", login_page.get_current_url())


import pytest

from utils.config_reader import ConfigReader


@pytest.mark.smoke
class TestPhenomLogin:

    def test_valid_login(self, login_page):

        # Step 1: Open Phenom application
        login_page.open(ConfigReader.BASE_URL)

        print("Phenom application opened successfully")

        # Step 2: Enter username
        login_page.enter_username(
            ConfigReader.USERNAME
        )

        print("Username submitted successfully")

        # Step 3: Enter password
        login_page.enter_password(
            ConfigReader.PASSWORD
        )

        print("Password submitted successfully")

        # Step 4: Wait for successful dashboard navigation
        login_page.page.wait_for_url(
            lambda url: url.startswith(
                "https://uat-pipeline.phenompeople.com"
            ),
            timeout=30000
        )

        # Assertion: Verify successful login
        assert "uat-pipeline.phenompeople.com" in login_page.get_current_url(), \
            "Login failed: CRM dashboard URL not found"

        print("Phenom CRM login successful")

        print("Current URL:", login_page.get_current_url())
