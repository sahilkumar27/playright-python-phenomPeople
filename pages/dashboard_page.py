from urllib.parse import urlsplit
from datetime import date, timedelta
import re
import time

from playwright.sync_api import Page, expect
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

        #Click on My meetings first page
        self.my_meetings_tab = self.page.get_by_text(
            "My meetings", exact=True
        ).first
        self.my_meetings_first_page = self.page.locator(
            "div.interview-row"
        ).first
        self.my_meetings_nav = self.page.get_by_text(
            "My Meetings", exact=True
        ).first



        self.meeting_rows = page.locator(".interview-row")




        #Click on My Activity
        self.my_meetings_Activity = self.page.locator(
            "//div[@id='crmUIBtnIntActivity']"
        )

        #Click on Preview Conversion
        self.preview_conversion = self.page.get_by_text(
            "Preview conversation", exact=False
        ).first

        #Meeting link inside preview conversation
        self.preview_conversation_modal = self.page.locator(
            "div.modal-dialog, [role='dialog']"
        ).filter(has_text="Preview Conversation").last
        self.preview_conversation_loader = self.preview_conversation_modal.locator(
            "app-loader .app-loader-cntr"
        )
        self.preview_email_frame = None
        self.meeting_link = None

        self.pending_scheduling = self.page.locator(
            "//span[text()='Pending scheduling']"
        ).nth(0)


        self.november_month = self.page.get_by_text(
            "November 2026", exact=True
        )
        self.november_13 = self.page.get_by_role(
            "gridcell", name="13", exact=True
        ).first
        self.time_2_to_230 = self.page.get_by_text(
            "2:00 PM - 2:30 PM", exact=True
        )
        self.schedule_button = self.page.get_by_role(
            "button", name="Schedule", exact=True
        )
        self.select_date_time_button = self.page.get_by_role(
            "button", name="Select date & time", exact=True
        )

    def search_candidate(self, candidate_name):
        self.global_search_input.wait_for(state="visible", timeout=30000)
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





    def click_first_meeting(self):
        for attempt in range(2):
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                row_count = self.meeting_rows.count()
                row_indexes = range(1, row_count) if row_count > 1 else range(row_count)
                for index in row_indexes:
                    row = self.meeting_rows.nth(index)
                    if row.is_visible() and row.is_enabled():
                        row.scroll_into_view_if_needed()
                        row.click()
                        print("Clicked the first meeting in My meetings")
                        return
                self.page.wait_for_timeout(500)
            if attempt == 0:
                self.page.reload(wait_until="domcontentloaded")
        raise TimeoutError("No visible meeting row appeared on the dashboard")

    def click_my_meetings_activity(self):
        self.my_meetings_Activity.wait_for(
            state="visible",
            timeout=15000
        )
        self.my_meetings_Activity.scroll_into_view_if_needed()
        self.my_meetings_Activity.evaluate("element => element.click()")
        self.page.wait_for_timeout(1000)
        print("Clicked on My Meetings Activity")


    def scroll_down(self, pixels=600):
        self.page.mouse.wheel(0, pixels)
        print(f"Scrolled down {pixels}px")








    def click_preview_conversion(self):
        self.preview_conversion.wait_for(
            state="visible",
            timeout=30000
        )
        self.preview_conversion.scroll_into_view_if_needed()
        self.preview_conversion.click(force=True)
        print("Clicked on Preview Conversation")



    def scroll_preview_conversation(self, pixels=500):
        self.preview_conversation_modal.wait_for(
            state="visible",
            timeout=15000
        )
        self.preview_conversation_loader.wait_for(
            state="hidden",
            timeout=30000
        )

        self.preview_conversation_modal.evaluate(
            """(element, pixels) => {
                const scrollable = [element, ...element.querySelectorAll("*")]
                    .filter(node => node.scrollHeight > node.clientHeight)
                    .sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
                if (!scrollable) {
                    throw new Error("Preview Conversation has no scrollable container");
                }
                scrollable.scrollTop = Math.min(
                    scrollable.scrollTop + pixels,
                    scrollable.scrollHeight - scrollable.clientHeight
                );
            }""",
            pixels
        )
        print(f"Scrolled Preview Conversation by {pixels}px")



    def open_meeting_link(self):
        iframe_locator = self.preview_conversation_modal.locator("iframe")
        iframe_locator.first.wait_for(state="attached", timeout=15000)
        self.preview_email_frame = iframe_locator.first.content_frame
        self.meeting_link = self.preview_email_frame.locator(
            "a[href*='phenomshorturl']"
        ).first
        for index in range(iframe_locator.count()):
            frame = iframe_locator.nth(index).content_frame
            candidate = frame.locator("a[href*='phenomshorturl']").first
            if candidate.count() > 0:
                self.preview_email_frame = frame
                self.meeting_link = candidate
                break

        self.preview_conversation_modal.evaluate(
            """element => {
                const scrollable = [element, ...element.querySelectorAll("*")]
                    .filter(node => node.scrollHeight > node.clientHeight)
                    .sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
                if (scrollable) {
                    scrollable.scrollTop = scrollable.scrollHeight;
                }
            }"""
        )
        with self.page.expect_popup() as popup_info:
            self.meeting_link.click()

        meeting_page = popup_info.value
        meeting_page.wait_for_load_state("domcontentloaded")
        meeting_page.wait_for_timeout(3000)
        print(
            "Opened meeting link in a new tab:",
            meeting_page.url,
            meeting_page.title()
        )
        return meeting_page

    def click_meeting_link(self):
        return self.open_meeting_link()


    def open_pending_scheduling(self):
        pending = self.page.get_by_text(
            "Hiring status automation run job", exact=True
        ).first
        pending.wait_for(state="visible", timeout=30000)
        group = pending.locator(
            "xpath=ancestor::div[contains(@class, 'cs-job-group')][1]"
        )
        header = group.locator("button.cs-job-group-header")
        if header.get_attribute("aria-expanded") != "true":
            header.click()

        request = group.locator("[id^='csRequestCard']").first
        request.wait_for(state="visible", timeout=30000)
        request.click()
        self.page.locator(".sh-loader-con").wait_for(
            state="hidden", timeout=30000
        )
        self.select_date_time_button.click()
        print("Opened first pending scheduling request")

    def select_date_and_time(self):
        preferred_date = date.today().replace(day=13)
        target_dates = [
            preferred_date + timedelta(days=offset) for offset in range(21)
        ]
        slot_pattern = re.compile(r"12:00\s+PM\s*-\s*12:30\s+PM")
        displayed_month = None

        for target_date in target_dates:
            month = self.page.get_by_text(
                target_date.strftime("%B %Y"), exact=True
            )
            if not month.is_visible():
                if displayed_month is None:
                    displayed_month = date.today().replace(day=1)
                while displayed_month < target_date.replace(day=1):
                    next_month = self.page.get_by_label(
                        re.compile(r"next month", re.IGNORECASE)
                    ).first
                    if not next_month.count():
                        next_month = self.page.locator(
                            "button[aria-label*='next' i], "
                            "button[title*='next' i]"
                        ).first
                    next_month.wait_for(state="visible", timeout=15000)
                    next_month.click()
                    displayed_month = (
                        displayed_month.replace(day=28) + timedelta(days=4)
                    ).replace(day=1)
                month.wait_for(state="visible", timeout=30000)
            else:
                displayed_month = target_date.replace(day=1)

            day_locators = self.page.get_by_role(
                "gridcell", name=str(target_date.day), exact=True
            )
            day_locator = None
            for index in range(day_locators.count()):
                candidate = day_locators.nth(index)
                if candidate.is_visible() and candidate.is_enabled():
                    day_locator = candidate
                    break
            if day_locator is None:
                print(
                    f"{target_date:%B} {target_date.day} is unavailable; "
                    "trying next day"
                )
                continue
            day_locator.click()

            time_locator = self.page.get_by_text(slot_pattern).first
            if time_locator.count() and time_locator.is_visible():
                time_locator.click()
                print(
                    f"Selected {target_date:%B} {target_date.day}, "
                    "12:00 PM - 12:30 PM"
                )
                return

            print(
                f"12:00 PM - 12:30 PM unavailable on "
                f"{target_date:%B} {target_date.day}; trying next day"
            )

        raise RuntimeError(
            "12:00 PM - 12:30 PM was unavailable from "
            f"{preferred_date:%B} {preferred_date.day} through "
            f"{target_dates[-1]:%B} {target_dates[-1].day}"
        )

    def click_schedule(self):
        self.schedule_button.wait_for(state="visible", timeout=15000)
        expect(self.schedule_button).to_be_enabled(timeout=15000)
        self.schedule_button.click()
        print("Clicked Schedule")

    def return_to_parent_tab(self, parent_page):
        self.page.wait_for_timeout(3000)
        self.page.close()
        parent_page.bring_to_front()
        print("Returned to parent dashboard tab")
