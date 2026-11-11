from base64 import urlsafe_b64decode
from datetime import date, timedelta
import json
import re
import time
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)

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

        self.select_date_time_button = self.page.get_by_role(
            "button", name="Select date & time", exact=True
        )


        #My Meetings - My Pending tab
        self.my_pending_tab = self.page.locator(
            "div[title='My pending']"
        )
        self.my_upcoming_tab = self.page.locator(
            "div[title='My upcoming']"
        )
        self.see_all_meeting_activities = self.page.get_by_role(
            "button", name="See all meeting activities", exact=True
        )
        #Click on three dot
        self.three_dot = self.page.locator(
            "button[id='crmUIBtnMoreInterviewActions0'] app-icon-more-vert-18px[class='pp-ds-button-bi'] svg path"
        )

        #Click on Cancel Meeting
        self.cancel_meeting = self.page.locator(
            "a#crmUIBtn0cancel-interview:visible"
        )

        #Select reason for cancellation
        self.cancel_reason_dropdown = self.page.locator(
            "#crmUIDpCancelReason"
        )
        self.cancel_reason_options = self.page.locator(
            "div[id^='crmUIDpCancelReason_select_']:visible"
        )

        #Yes, Cancel meeting button
        self.yes_cancel_meeting_button = self.page.locator(
            "//span[normalize-space()='Yes, Cancel meeting']"
        )

        self.meeting_rows = self.page.locator(".interview-row")


    def _wait_for_scheduler_idle(self):
        self.page.wait_for_function(
            """() => [...document.querySelectorAll('.sh-loader-con')].every(
                element => {
                    const style = window.getComputedStyle(element);
                    return style.display === 'none' ||
                        style.visibility === 'hidden' ||
                        element.getClientRects().length === 0;
                }
            )""",
            timeout=30000,
        )

    def _wait_for_dashboard_idle(self):
        self.page.wait_for_function(
            """() => [...document.querySelectorAll('.app-loader-cntr')].every(
                element => {
                    const style = window.getComputedStyle(element);
                    return style.display === 'none' ||
                        style.visibility === 'hidden' ||
                        element.getClientRects().length === 0;
                }
            )""",
            timeout=45000,
        )

    def search_candidate(self, candidate_name):
        self.global_search_input.wait_for(state="visible", timeout=30000)
        for attempt in range(3):
            self.global_search_input.fill(candidate_name)
            self.page.wait_for_timeout(750)
            self.global_search_input.press("Enter")
            try:
                self.candidate_search_result.wait_for(
                    state="visible", timeout=15000
                )
                break
            except PlaywrightTimeoutError:
                if attempt == 2:
                    raise
                self.global_search_input.fill("")
                self.page.wait_for_timeout(1000)

        # Close search suggestions
        self.page.keyboard.press("Escape")

    def get_search_results(self):
        self.candidate_search_result.scroll_into_view_if_needed()
        self.candidate_search_result.click(force=True)
        print("First candidate selected successfully")

    def open_candidate_profile(self):
        try:
            self.open_candidate_profile_link.wait_for(
                state="visible", timeout=30000
            )
        except PlaywrightTimeoutError:
            # Selecting a search result can race the candidate detail panel.
            # Re-select it once so the external profile action is rendered.
            self.candidate_search_result.wait_for(
                state="visible", timeout=15000
            )
            self.candidate_search_result.click(force=True)
            self.open_candidate_profile_link.wait_for(
                state="visible", timeout=30000
            )

        self.open_candidate_profile_link.click()

        print("Clicked external candidate profile link")





    def open_meeting_by_title(self, meeting_title):
        row = self.meeting_row(meeting_title)
        row.wait_for(state="visible", timeout=30000)
        row.click()
        print(f"Opened meeting '{meeting_title}'")

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
        self.preview_conversation_modal.wait_for(
            state="visible", timeout=30000
        )
        self.preview_conversation_loader.wait_for(
            state="hidden", timeout=45000
        )
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
        self.meeting_link.wait_for(state="attached", timeout=15000)
        meeting_url = self.meeting_link.get_attribute("href")
        if not meeting_url:
            raise RuntimeError("The interview scheduling email has no link")
        meeting_page = self.page.context.new_page()
        meeting_page.goto(meeting_url, wait_until="domcontentloaded")
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

    def _email_frame_with_subject(self, subject_fragment):
        frames = [
            frame for frame in self.page.frames
            if frame != self.page.main_frame
        ]
        for frame in frames:
            body = frame.locator("body")
            if body.count() and subject_fragment in body.inner_text(timeout=5000):
                return body
        return None

    def verify_email_subject(self, subject):
        subject_pattern = re.compile(
            rf"Subject\s*:\s*{re.escape(subject)}", re.IGNORECASE
        )
        body = self._email_frame_with_subject(subject)
        container = body or self.preview_conversation_modal
        expect(container).to_contain_text(subject_pattern)
        print("Verified email subject:", subject)

    def verify_confirmation_email(self, candidate_name, job_title):
        subject = f"Interview Confirmation - {candidate_name} - {job_title}"
        self.verify_email_subject(subject)

    def click_my_upcoming_tab(self):
        self.my_upcoming_tab.wait_for(state="visible", timeout=30000)
        self._wait_for_dashboard_idle()
        self.my_upcoming_tab.click()
        print("Opened My Upcoming tab")

    def wait_for_meeting_tabs(self):
        self.my_pending_tab.wait_for(state="visible", timeout=30000)
        self.my_upcoming_tab.wait_for(state="visible", timeout=30000)

    def meeting_row(self, meeting_title):
        return self.meeting_rows.filter(has_text=meeting_title).first

    def open_all_meeting_activities(self, meeting_title=None, status=None):
        try:
            self.see_all_meeting_activities.wait_for(
                state="visible", timeout=30000
            )
        except PlaywrightTimeoutError:
            pass

        if self.see_all_meeting_activities.is_visible():
            self.see_all_meeting_activities.click()
            self.page.get_by_text(
                "All meeting activities", exact=True
            ).wait_for(state="visible", timeout=30000)
            print("Opened all meeting activities")

        if status == "all":
            all_meetings = self.page.get_by_text(
                "All meetings", exact=True
            ).last
            all_meetings.wait_for(state="visible", timeout=15000)
            all_meetings.evaluate(
                "element => (element.closest('li') || element).click()"
            )
            self.page.wait_for_timeout(500)

        if meeting_title:
            search = self.page.get_by_role(
                "textbox", name="Search", exact=True
            ).last
            search.wait_for(state="visible", timeout=30000)
            search.fill(meeting_title)
            search.press("Enter")
            self.meeting_row(meeting_title).wait_for(
                state="visible", timeout=30000
            )
            print(f"Found meeting activity '{meeting_title}'")

    def verify_meeting_in_upcoming(self, meeting_title, scheduled_slot):
        row = self.meeting_row(meeting_title)
        scheduled_day = scheduled_slot["date"].strftime("%b %-d")
        start_time = scheduled_slot["time"].split("-")[0].strip()
        deadline = time.monotonic() + 60
        row_text = ""
        activity_url = self.page.url

        while time.monotonic() < deadline:
            if row.is_visible():
                row_text = row.inner_text()
                if (
                    scheduled_day in row_text
                    and start_time in row_text
                    and re.search(r"\bUpcoming\b", row_text, re.IGNORECASE)
                ):
                    print(
                        f"Verified '{meeting_title}' in My Upcoming with slot "
                        f"{scheduled_day}, {scheduled_slot['time']}"
                    )
                    return

            self.page.wait_for_timeout(5000)
            self.page.goto(activity_url, wait_until="domcontentloaded")
            search = self.page.get_by_role(
                "textbox", name="Search", exact=True
            ).last
            search.wait_for(state="visible", timeout=15000)
            search.fill(meeting_title)
            search.press("Enter")
            row = self.meeting_row(meeting_title)

        raise AssertionError(
            f"Meeting '{meeting_title}' did not reach Upcoming at "
            f"{scheduled_day}, {scheduled_slot['time']} within 60 seconds. "
            f"Last row text: {row_text!r}"
        )

    def open_meeting_activity(self, meeting_title):
        row = self.meeting_row(meeting_title)
        row.wait_for(state="visible", timeout=15000)
        row.click()
        self.click_my_meetings_activity()
        self.click_preview_conversion()
        self.preview_conversation_modal.wait_for(
            state="visible", timeout=15000
        )

    def open_pending_scheduling(self, meeting_title, job_title):
        pending = self.page.get_by_text(
            job_title, exact=True
        ).first
        pending.wait_for(state="visible", timeout=30000)
        group = pending.locator(
            "xpath=ancestor::div[contains(@class, 'cs-job-group')][1]"
        )
        header = group.locator("button.cs-job-group-header")
        if header.get_attribute("aria-expanded") != "true":
            header.click()

        requests = group.locator("[id^='csRequestCard']")
        request_id = self._scheduling_request_id()
        matching_request = (
            requests.filter(has_text=meeting_title).first
            if meeting_title
            else requests.first
        )
        if matching_request.count() == 0 and request_id:
            matching_request = group.locator(f"[id*='{request_id}']").first
        request = (
            matching_request
            if matching_request.count()
            else requests.first
        )
        request.wait_for(state="visible", timeout=30000)
        request.click()
        self.page.locator(".sh-loader-con").wait_for(
            state="hidden", timeout=30000
        )
        if self.select_date_time_button.is_visible():
            self.select_date_time_button.click()
        else:
            reschedule_action = self.page.get_by_role(
                "button",
                name=re.compile(r"reschedul|change time|change date", re.IGNORECASE),
            ).first
            if reschedule_action.is_visible():
                reschedule_action.click()
            else:
                print(
                    "Scheduling request details:",
                    self.page.locator("body").inner_text(timeout=10000)[:2000],
                )
        print("Opened pending scheduling request")

    def _scheduling_request_id(self):
        token = parse_qs(urlsplit(self.page.url).query).get("llt", [None])[0]
        if not token:
            return None
        try:
            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            return json.loads(urlsafe_b64decode(payload)).get(
                "schedulingRequestId"
            )
        except (IndexError, ValueError, json.JSONDecodeError):
            return None

    def select_date_and_time(self, after_date=None):
        today = date.today()
        start_offset = 1
        if after_date and after_date >= today:
            start_offset = (after_date - today).days + 1
        target_dates = [
            today + timedelta(days=offset)
            for offset in range(start_offset, 61)
        ]
        slot_pattern = re.compile(
            r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\s*-\s*"
            r"\d{1,2}:\d{2}\s*(?:AM|PM)\b",
            re.IGNORECASE,
        )
        displayed_month = today.replace(day=1)

        for target_date in target_dates:
            self._wait_for_scheduler_idle()
            month = self.page.get_by_text(
                target_date.strftime("%B %Y"), exact=True
            )
            if not month.is_visible():
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
                if (
                    candidate.is_visible()
                    and candidate.is_enabled()
                    and candidate.get_attribute("aria-disabled") != "true"
                ):
                    day_locator = candidate
                    break
            if day_locator is None:
                print(
                    f"{target_date:%B} {target_date.day} is unavailable; "
                    "trying next day"
                )
                continue
            day_locator.click()
            self._wait_for_scheduler_idle()
            slots = self.page.get_by_text(slot_pattern)
            available_slots = []
            for index in range(slots.count()):
                time_locator = slots.nth(index)
                if time_locator.is_visible() and time_locator.is_enabled():
                    available_slots.append(time_locator)
            if available_slots:
                time_locator = available_slots[-1]
                slot_name = time_locator.inner_text().strip()
                time_locator.click()
                print(
                    f"Selected {target_date:%B} {target_date.day}, "
                    f"{slot_name}"
                )
                return {"date": target_date, "time": slot_name}
            else:
                print(
                    f"No available time slots on {target_date:%B} "
                    f"{target_date.day}; trying next day"
                )

        raise RuntimeError(
            "No available time slot found from "
            f"{today:%B} {today.day} through "
            f"{target_dates[-1]:%B} {target_dates[-1].day}"
        )

    def click_schedule(self, expected_slot=None, verify_slot=True):
        body = self.page.locator("body")
        success_message = re.compile(
            r"Interview scheduled|scheduled successfully", re.IGNORECASE
        )

        for attempt in range(4):
            schedule_action = self.page.get_by_role(
                "button",
                name=re.compile(r"^(?:re)?schedule$", re.IGNORECASE),
            ).first
            schedule_action.wait_for(state="visible", timeout=15000)
            expect(schedule_action).to_be_enabled(timeout=15000)
            action_name = schedule_action.inner_text().strip()
            schedule_action.click()
            print(f"Clicked {action_name}")

            try:
                expect(body).to_contain_text(
                    success_message, timeout=15000
                )
            except AssertionError:
                body_text = body.inner_text(timeout=10000)
                if (
                    "No slots available" not in body_text
                    or expected_slot is None
                    or attempt == 3
                ):
                    raise RuntimeError(
                        "Scheduler did not confirm the selected slot. "
                        f"Response: {body_text[:800]}"
                    )
                expected_slot = self.select_date_and_time(
                    after_date=expected_slot["date"]
                )
                continue

            expect(body).to_contain_text(
                re.compile(r"confirmation email has been sent", re.I),
                timeout=10000,
            )

            if expected_slot and verify_slot:
                month, day = expected_slot["date"].strftime("%b %d").split()
                try:
                    # A reschedule page can still show the previous success
                    # panel while the update is being processed. Wait for the
                    # confirmation itself to reflect the newly selected slot.
                    expect(body).to_contain_text(
                        re.compile(rf"{re.escape(month)}\s*{int(day)}", re.I),
                        timeout=30000,
                    )
                    expect(body).to_contain_text(
                        expected_slot["time"], timeout=10000
                    )
                except AssertionError:
                    body_text = body.inner_text(timeout=10000)
                    if action_name.lower() == "reschedule" and attempt < 3:
                        print(
                            "Reschedule confirmation still shows the previous "
                            "slot; selecting another available slot."
                        )
                        expected_slot = self.reschedule_scheduled_meeting(
                            expected_slot
                        )
                        continue
                    raise AssertionError(
                        "Scheduler did not confirm the selected slot "
                        f"{expected_slot!r}. Response: {body_text[:800]}"
                    )
            print("Scheduler response:", body.inner_text(timeout=10000)[:1000])
            return expected_slot

        raise RuntimeError("Unable to schedule after four slot attempts")

    def reschedule_scheduled_meeting(self, original_slot=None):
        reschedule_link = self.page.get_by_text(
            "Reschedule", exact=True
        ).last
        reschedule_link.wait_for(state="visible", timeout=15000)
        expect(self.page.locator("body")).to_contain_text(
            "Want to make any changes?", timeout=10000
        )
        original_page = self.page
        existing_pages = set(self.page.context.pages)
        href = reschedule_link.get_attribute("href")
        reschedule_link.click()
        self.page.wait_for_timeout(1000)
        new_pages = [
            page for page in original_page.context.pages
            if page not in existing_pages
        ]
        if new_pages:
            self.page = new_pages[-1]
            self.page.wait_for_load_state("domcontentloaded")
            self.page.bring_to_front()
            original_page.close()
            self.__init__(self.page)

        if self.select_date_time_button.is_visible():
            self.select_date_time_button.click()
        elif (
            not self.page.get_by_role("gridcell").first.is_visible()
            and not self.page.get_by_text(
                re.compile(
                    r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\b",
                    re.IGNORECASE,
                )
            ).first.is_visible()
        ):
            print(
                "Reschedule action details:",
                {"url": self.page.url, "href": href},
                self.page.locator("body").inner_text(timeout=10000)[:1500],
            )
            raise RuntimeError(
                "Reschedule action did not open date and time selection"
            )
        print("Opened the scheduled interview's reschedule flow")
        original_date = original_slot["date"] if original_slot else None
        return self.select_date_and_time(after_date=original_date)

    def return_to_parent_tab(self, parent_page):
        self.page.wait_for_timeout(3000)
        self.page.close()
        parent_page.bring_to_front()
        print("Returned to parent dashboard tab")


    #Cancel the meeting from the dashboard page - under pending tab and verify that the meeting is cancelled under my meeting tab
    def click_my_pending_tab(self):
        self.my_pending_tab.wait_for(state="visible", timeout=30000)
        self._wait_for_dashboard_idle()
        self.my_pending_tab.click(force=True)
        print("Clicked on My Pending tab")


    def click_three_dot(self, meeting_title=None):
        if meeting_title:
            row = self.meeting_row(meeting_title)
            row.wait_for(state="visible", timeout=15000)
            button = row.locator("button[id*='MoreInterviewActions']").first
        else:
            button = self.three_dot
        button.wait_for(state="visible", timeout=15000)
        button.click(force=True)
        print("Clicked on three dot menu")

    def click_cancel_meeting(self):
        self.cancel_meeting.wait_for(state="visible", timeout=15000)
        self.cancel_meeting.click()
        print("Clicked on Cancel Meeting")

    def select_cancel_reason(self):
        self.cancel_reason_dropdown.wait_for(state="visible", timeout=15000)
        self.cancel_reason_dropdown.click()

        self.cancel_reason_options.first.wait_for(
            state="visible", timeout=10000
        )
        preferred_reason = self.cancel_reason_options.filter(
            has_text="Candidate is withdrawn from the job"
        ).first
        option = (
            preferred_reason
            if preferred_reason.count()
            else self.cancel_reason_options.first
        )
        reason_text = option.inner_text().strip()
        option.click()
        print("Selected cancellation reason:", reason_text)

    def click_yes_cancel_meeting(self):
        self.yes_cancel_meeting_button.wait_for(state="visible", timeout=15000)
        self.yes_cancel_meeting_button.click(force=True)
        print("Clicked on Yes, Cancel meeting button")


    #Get the status of a meeting by its title
    def get_meeting_status(self, meeting_title, expected_status="Cancelled"):

        meeting_row = self.meeting_rows.filter(
            has_text=meeting_title
        ).first

        meeting_row.wait_for(
            state="visible",
            timeout=15000
        )

        status = meeting_row.get_by_text(expected_status, exact=True)

        return status
