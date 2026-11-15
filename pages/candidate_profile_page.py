
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .base_page import BasePage


class CandidateProfilePage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

        self.more_options_button = page.locator(
            "#interview-module-options"
        )

        self.invite_to_job_interview = page.locator(
            "//span[text()='Invite to Job Interview']"
        )

        self.single_meeting_option = page.locator(
            "#crmUIBtnSubCategorypanel"
        )

    def click_more_options(self):

        try:
            self.more_options_button.wait_for(
                state="visible",
                timeout=30000
            )

        except PlaywrightTimeoutError:
            self.page.reload(
                wait_until="domcontentloaded"
            )

        self.click(self.more_options_button)

        print("Clicked three-dot menu")

    def click_invite_to_job_interview(self):

        self.click(self.invite_to_job_interview)

        print("Selected Invite to Job Interview")

    def click_single_meeting(self):

        self.click(self.single_meeting_option)

        print("Selected Single Meeting")
