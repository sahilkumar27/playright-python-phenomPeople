#
# from playwright.sync_api import Page
# from .base_page import BasePage
#
#
# class CandidateProfilePage(BasePage):
#
#     def __init__(self, page: Page):
#         super().__init__(page)
#
#         # Three-dot menu in candidate profile
#         self.more_options_button = page.locator(
#             "#interview-module-options"
#         )
#
#     def click_more_options(self):
#
#         self.more_options_button.wait_for(
#             state="visible",
#             timeout=15000
#         )
#
#         self.more_options_button.click()
#
#         print("Clicked candidate profile three-dot menu")


from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from .base_page import BasePage


class CandidateProfilePage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

        # Three-dot menu
        self.more_options_button = page.locator(
            "#interview-module-options"
        )

        # Invite to Job Interview option
        self.invite_to_job_interview = page.locator(
            "//span[text()='Invite to Job Interview']"
        )

        # Single Meeting option
        self.single_meeting_option = page.locator(
            "#crmUIBtnSubCategorypanel"
        )

    def click_more_options(self):
        self.page.wait_for_load_state("domcontentloaded")
        try:
            self.more_options_button.wait_for(state="visible", timeout=30000)
        except PlaywrightTimeoutError:
            self.page.reload(wait_until="domcontentloaded")
            self.more_options_button.wait_for(state="visible", timeout=30000)

        self.more_options_button.click()

        print("Clicked candidate profile three-dot menu")

    def click_invite_to_job_interview(self):

        self.invite_to_job_interview.wait_for(
            state="visible",
            timeout=15000
        )

        self.invite_to_job_interview.click()
        print("Selected Invite to Job Interview")


    def click_single_meeting(self):
        self.single_meeting_option.wait_for(
            state="visible",
            timeout=15000
        )

        self.single_meeting_option.click()

        print("Selected Single Meeting")