from playwright.sync_api import Page
from .base_page import BasePage
from pages.candidate_profile_page import CandidateProfilePage

class DashboardPage:
    """Handles Phenom CRM Dashboard operations."""

    def __init__(self, page: Page):
        self.page = page

        # Global Search
        self.global_search_input = page.locator("#global-search-input")

        # First candidate card under search results
        self.candidate_search_result = page.locator(
            ".search-lists-cntr .lists-body-cntr"
        ).first

        # External candidate profile link (arrow icon)
        self.open_candidate_profile_link = self.page.locator(
            "#crmUiLinkNewTab"
        )


    def search_candidate(self, candidate_name):

        self.global_search_input.fill(candidate_name)
        self.global_search_input.press("Enter")

        # Wait for the first candidate result
        self.candidate_search_result.wait_for(
            state="visible",
            timeout=15000
        )

        # Close search suggestions
        self.page.keyboard.press("Escape")

    def get_search_results(self):
        self.candidate_search_result.click()
        print("First candidate selected successfully")

    def open_candidate_profile(self):
        self.open_candidate_profile_link.wait_for(
            state="visible",
            timeout=15000
        )

        self.open_candidate_profile_link.click()

        print("Clicked external candidate profile link")
