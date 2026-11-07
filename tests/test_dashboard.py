import pytest

from utils.config_reader import ConfigReader
from pages.candidate_profile_page import CandidateProfilePage

@pytest.mark.e2e
class TestDashboard:

    def test_search_candidate(self, login_page, dashboard_page):

        # Step 1: Open Phenom and Login
        login_page.open(ConfigReader.BASE_URL)
        login_page.login(
            ConfigReader.USERNAME,
            ConfigReader.PASSWORD
        )

        # Step 2: Wait for Dashboard
        login_page.page.wait_for_url(
            lambda url: url.startswith(
                "https://uat-pipeline.phenompeople.com"
            ),
            timeout=30000
        )

        print("Successfully navigated to Dashboard")
        print("Current URL:", login_page.get_current_url())

        login_page.page.wait_for_timeout(5000)

        # Step 3: Search Candidate
        dashboard_page.search_candidate("Pavan Chittala")
        print("Searching for Pavan Chittala")

        dashboard_page.get_search_results()
        print("Clicked first Pavan Chittala candidate")

        # Step 4: Select First Candidate
        dashboard_page.get_search_results()

        print("First candidate selected successfully")

        # Step 5: Open Candidate Profile in New Tab
        with login_page.page.expect_popup() as popup_info:
            dashboard_page.open_candidate_profile()

        candidate_profile_tab = popup_info.value

        candidate_profile_tab.wait_for_load_state("domcontentloaded")

        print("Candidate profile opened successfully")
        print("Candidate Profile URL:", candidate_profile_tab.url)

        # Step 6: Initialize Candidate Profile Page
        candidate_profile_page = CandidateProfilePage(candidate_profile_tab)

        # Step 7: Click Three-Dot Menu
        candidate_profile_page.click_more_options()

        # Step 8: Select Invite to Job Interview
        candidate_profile_page.click_invite_to_job_interview()

        print("Invite to Job Interview selected")

        # Step 9: Keep browser open
        input("Press ENTER in PyCharm console to close the browser...")