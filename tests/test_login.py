import pytest

from utils.config_reader import ConfigReader


@pytest.mark.smoke
class TestPhenomLogin:

    def test_user_can_log_in(self, login_page):

        # Step 1: Open Phenom application
        login_page.open(ConfigReader.BASE_URL)

        # Step 2: Enter username
        login_page.enter_email(
            ConfigReader.USERNAME
        )

        # Step 3: Enter password
        login_page.enter_password(
            ConfigReader.PASSWORD
        )

        login_page.continue_button.click()

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


