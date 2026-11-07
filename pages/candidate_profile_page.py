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


from playwright.sync_api import Page
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

    def click_more_options(self):

        self.more_options_button.wait_for(
            state="visible",
            timeout=15000
        )

        self.more_options_button.click()

        print("Clicked candidate profile three-dot menu")

    def click_invite_to_job_interview(self):

        self.invite_to_job_interview.wait_for(
            state="visible",
            timeout=15000
        )

        self.invite_to_job_interview.click()

        print("Selected Invite to Job Interview")