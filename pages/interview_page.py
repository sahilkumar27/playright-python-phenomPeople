
from pathlib import Path
from urllib.parse import urljoin
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from .base_page import BasePage


class InterviewPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

        # Meeting Title
        self.meeting_title_input = page.locator(
            "//input[@id='crmUITxtInterviewTitle']"
        )

        # Meeting title counter file
        self.counter_file = (
            Path(__file__).resolve().parent.parent
            / "resources"
            / "meeting_infoTitle"
        )

        # Interviewer Search
        self.interviewer_input = page.locator("#crmUiDpInterviewerInput")
        self.interviewer_dropdown = page.locator(
            "app-search-interviewers-dropdown"
        )


        #Meeting type
        self.metting_type = page.locator("//span[normalize-space()='Online']")


        #Select Channel
        self.select_channel = page.locator(
            "//div[normalize-space()='Select a channel']"
        )
        self.google_meet_option = page.locator(
            "a"
        ).filter(has_text="Google Meet").first

        #Select Duration
        self.select_duration = page.locator(
            "//div[normalize-space()='Select duration']"
        )

        self.duration_30_min = page.get_by_role(
            "link", name="30 min", exact=True
        ).first

        self.next_button = page.locator("#crmUIBtnNext")


        # Date and time scheduling controls
        self.schedule_within_option = page.get_by_text(
            "Schedule within", exact=True
        )
        self.schedule_within_days = page.get_by_role(
            "spinbutton", name="Enter number"
        )

        # Communication - unselect SMS notification
        self.sms_checkbox = page.locator(
            "#communicationChannelSMSNotification"
        )
        self.sms_checkbox_label = page.locator(
            "label[for='communicationChannelSMSNotification']"
        )

        #Click on send invite button
        self.send_invite_button = page.locator(
            "//span[normalize-space()='Send invite']"
        )

        #Click on got it button
        self.ok_got_it_button = page.locator(
            "//span[text()='Ok, Got It']"
        )

        #Navigate to dashboard page
        self.dashboard_link = page.locator(
            "//a[@id='crmAutoEventsNavDashboardPage']"
        )



    # Generate sequential meeting title
    def generate_meeting_title(self):
        counter_value = self.counter_file.read_text().strip()
        current_number = int(counter_value) if counter_value else 0

        next_number = current_number + 1

        self.counter_file.write_text(str(next_number))

        meeting_title = f"Tester{next_number}"

        self.meeting_title_input.wait_for(
            state="visible",
            timeout=30000
        )

        self.meeting_title_input.fill(meeting_title)

        print("Meeting title:", meeting_title)

        return meeting_title

    def search_interviewer(self, interviewer_email):
        self.interviewer_input.wait_for(state="visible", timeout=15000)

        self.interviewer_input.fill(interviewer_email)

        self.page.locator(
            "app-scorecard-selector .app-loader-cntr"
        ).wait_for(state="hidden", timeout=15000)

        first_interviewer_option = self.interviewer_dropdown.get_by_text(
            "Aarthi Mupparthy", exact=True
        ).first
        first_interviewer_option.wait_for(
            state="visible",
            timeout=15000
        )

        first_interviewer_option.click()

        print("Selected interviewer:", interviewer_email)


    def click_meeting_type(self):
        self.metting_type.wait_for(state="visible", timeout=15000)
        self.metting_type.click()

    def select_meeting_channel(self):
        self.select_channel.wait_for(state="visible", timeout=15000)
        self.select_channel.click()

        self.google_meet_option.wait_for(
                state="visible",
                timeout=10000
            )
        self.google_meet_option.click()

        print("Selected meeting channel: Google Meet")

    def select_duration_and_continue(self):
        # Scroll to Duration dropdown
        self.select_duration.scroll_into_view_if_needed()

        # Open Duration dropdown
        self.select_duration.wait_for(state="visible", timeout=15000)
        self.select_duration.click()

        # Select 30 minutes
        self.duration_30_min.wait_for(state="visible", timeout=10000)
        self.duration_30_min.click()

        print("Selected meeting duration: 30 min")

        # Click Next
        self.next_button.wait_for(state="visible", timeout=10000)
        self.next_button.click()

        print("Clicked Next button")

    #Second page of interview scheduling, verify date and time and click next
    def verify_date_time_and_continue(self):
        self.schedule_within_option.wait_for(
            state="visible",
            timeout=15000
        )

        print("Schedule within option is visible")

        self.next_button.wait_for(
            state="visible",
            timeout=10000
        )

        self.next_button.click()

        print("Clicked Next button on Date and Time page")

    def configure_communication_and_send_invite(self):
        # Wait for the Communication page to load
        self.page.wait_for_timeout(4000)

        # The input is visually hidden and may be disabled; the label owns the
        # application's custom checkbox interaction.
        self.sms_checkbox.wait_for(
            state="attached",
            timeout=15000
        )
        self.sms_checkbox_label.wait_for(
            state="visible",
            timeout=15000
        )
        if self.sms_checkbox_label.get_attribute("class") and "checked" in (
            self.sms_checkbox_label.get_attribute("class") or ""
        ):
            self.sms_checkbox_label.click(force=True)
            self.page.wait_for_function(
                """selector => {
                    const label = document.querySelector(selector);
                    return label && !label.classList.contains("checked");
                }""",
                arg="label[for='communicationChannelSMSNotification']",
                timeout=5000
            )
        print("SMS notification unselected")

        # Click Send invite
        self.send_invite_button.wait_for(
            state="visible",
            timeout=15000
        )
        self.send_invite_button.click()

        print("Clicked Send invite")

        try:
            self.ok_got_it_button.wait_for(state="visible", timeout=10000)
            self.ok_got_it_button.click()
            print("Clicked Ok, Got It button")
        except PlaywrightTimeoutError:
            # Some environments complete the send without displaying a dialog.
            self.page.wait_for_timeout(2000)
            print("Invite confirmation dialog was not displayed")

    def navigate_to_dashboard(self):
        if self.ok_got_it_button.is_visible():
            self.ok_got_it_button.click()
            print("Closed invite confirmation")

        dashboard_href = self.dashboard_link.get_attribute("href")
        if dashboard_href:
            dashboard_url = urljoin(self.page.url, dashboard_href)
        else:
            dashboard_url = self.page.url.split("/dashboard", 1)[0] + "/dashboard"
        self.page.goto(dashboard_url, wait_until="domcontentloaded")
        self.page.wait_for_url(
            lambda url: "/dashboard" in url,
            timeout=30000
        )
        print("Navigated to Dashboard page")
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
