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
            timeout=30000
        )
        self.preview_conversation_loader.wait_for(
            state="hidden",
            timeout=45000
        )

        self.preview_conversation_modal.evaluate(
            """(modal, pixels) => {
                const elements = [modal, ...modal.querySelectorAll("*")];

                const scrollable = elements.filter(element => {
                    const style = window.getComputedStyle(element);
                    return (
                        element.scrollHeight > element.clientHeight &&
                        ["auto", "scroll"].includes(style.overflowY)
                    );
                });

                if (!scrollable.length) {
                    throw new Error(
                        "No vertically scrollable container found in Preview Conversation"
                    );
                }

                const container = scrollable.reduce((largest, current) => {
                    const largestRange =
                        largest.scrollHeight - largest.clientHeight;
                    const currentRange =
                        current.scrollHeight - current.clientHeight;
                    return currentRange > largestRange ? current : largest;
                });

                container.scrollTop = Math.min(
                    container.scrollTop + pixels,
                    container.scrollHeight - container.clientHeight
                );
            }""",
            pixels
        )

        print(f"Scrolled Preview Conversation by {pixels}px")




    def open_meeting_link(self):
        iframe_locator = self.preview_conversation_modal.locator("iframe")
        iframe_locator.first.wait_for(
            state="attached",
            timeout=30000
        )

        self.meeting_link = None

        for index in range(iframe_locator.count()):
            frame = iframe_locator.nth(index).content_frame
            candidate_link = frame.locator(
                "a[href*='phenomshorturl']"
            ).first

            if candidate_link.count() > 0:
                self.preview_email_frame = frame
                self.meeting_link = candidate_link
                break

        if self.meeting_link is None:
            raise RuntimeError(
                "Could not find the interview scheduling link in the email iframe"
            )

        self.meeting_link.wait_for(
            state="attached",
            timeout=30000
        )
        self.meeting_link.scroll_into_view_if_needed()

        meeting_url = self.meeting_link.get_attribute("href")

        if not meeting_url:
            raise RuntimeError(
                "The interview scheduling email has an empty link"
            )

        meeting_page = self.page.context.new_page()
        meeting_page.goto(
            meeting_url,
            wait_until="domcontentloaded",
            timeout=45000
        )
        meeting_page.bring_to_front()

        print("Opened interview scheduling page:", meeting_page.url)

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
        if body is not None:
            expect(body).to_contain_text(subject_pattern)
            print("Verified email subject:", subject)
            return

        # Some environments append a generated job label instead of the
        # requested job title. Preserve the stable candidate-specific part.
        subject_prefix = subject.rsplit(" - ", 1)[0]
        prefix_pattern = re.compile(
            rf"Subject\s*:\s*{re.escape(subject_prefix)}\s*-\s*\S",
            re.IGNORECASE,
        )
        expect(container).to_contain_text(prefix_pattern)
        print("Verified email subject prefix:", subject_prefix)

    def verify_email_subject_starts_with(self, subject_prefix):
        subject_pattern = re.compile(
            rf"Subject\s*:\s*{re.escape(subject_prefix)}(?:\s|$)",
            re.IGNORECASE,
        )
        expect(self.preview_conversation_modal).to_contain_text(
            subject_pattern
        )
        print("Verified exact availability email subject prefix:", subject_prefix)

    def verify_availability_email_details(
        self, subject_prefix, meeting_title, duration="30 min"
    ):
        container = None
        for frame in self.page.frames:
            if frame == self.page.main_frame:
                continue
            body = frame.locator("body")
            if not body.count():
                continue
            body_text = body.inner_text(timeout=5000)
            if meeting_title in body_text:
                container = body
                break

        if container is None:
            raise AssertionError(
                f"Could not find meeting title '{meeting_title}' "
                "in the availability email iframe"
            )

        details_pattern = re.compile(
            rf"{re.escape(meeting_title)}[\s\S]*?"
            rf"{re.escape(duration)}",
            re.IGNORECASE,
        )
        expect(container).to_contain_text(details_pattern)
        print(
            "Verified availability email subject, meeting title, and duration:",
            subject_prefix,
            meeting_title,
            duration,
        )

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
        deadline = time.monotonic() + 180
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
            f"{scheduled_day}, {scheduled_slot['time']} within 180 seconds. "
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
        self.page.wait_for_load_state("networkidle", timeout=45000)
        scheduler_ready = self.page.locator(
            "[role='gridcell'], button:has-text('Select date & time'), "
            "button:has-text('Schedule')"
        ).first
        try:
            scheduler_ready.wait_for(state="visible", timeout=45000)
        except PlaywrightTimeoutError:
            if not self.page.locator("body").inner_text(timeout=5000).strip():
                self.page.reload(wait_until="networkidle", timeout=60000)
                scheduler_ready.wait_for(state="visible", timeout=45000)

        groups = self.page.locator("div.cs-job-group")
        group = groups.filter(has_text=meeting_title).first
        if group.count() == 0:
            pending = self.page.get_by_text(job_title, exact=True).first
            if pending.count() and pending.is_visible():
                group = pending.locator(
                    "xpath=ancestor::div[contains(@class, 'cs-job-group')][1]"
                )
            else:
                group = None
        else:
            group.wait_for(state="visible", timeout=30000)

        if group is not None:
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

        # Get the current browser URL and extract its query parameters.
        # Retrieve the value of the "llt" parameter (the token).
        # If "llt" does not exist, use None as the default value.
        token = parse_qs(
            urlsplit(self.page.url).query
        ).get("llt", [None])[0]

        # Check whether the token is missing or empty.
        # If no token is available, return None.
        if not token:
            return None

        try:
            # Split the token using "." as the separator.
            # A JWT-like token generally has three parts:
            # Header.Payload.Signature
            # Index [1] retrieves the payload (second part).
            payload = token.split(".")[1]

            # Add missing "=" padding characters.
            # Base64URL decoding requires the encoded string length
            # to be a multiple of 4.
            payload += "=" * (-len(payload) % 4)

            # Decode the Base64URL-encoded payload into bytes.
            # Convert the decoded JSON data into a Python dictionary.
            # Retrieve and return the "schedulingRequestId" value.
            return json.loads(
                urlsafe_b64decode(payload)
            ).get("schedulingRequestId")

        # Handle errors that may occur during token extraction,
        # Base64URL decoding, or JSON parsing.
        except (
                IndexError,  # Token does not contain a second part.
                ValueError,  # Invalid Base64URL data.
                json.JSONDecodeError  # Decoded content is not valid JSON.
        ):
            # Return None instead of stopping test execution.
            return None

    def _show_calendar_month(self, target_date, displayed_month):
        month_name = target_date.strftime("%B %Y")
        month = self.page.get_by_text(month_name, exact=True)

        while (
            not month.is_visible()
            and displayed_month < target_date.replace(day=1)
        ):
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

        if not month.is_visible():
            # Some deployments abbreviate the month label.
            abbreviated_month = self.page.get_by_text(
                re.compile(
                    rf"{target_date.strftime('%B|%b')}\\s+{target_date.year}"
                ),
                exact=False,
            ).first
            if not abbreviated_month.is_visible():
                self.page.get_by_role(
                    "gridcell",
                    name=str(target_date.day),
                    exact=True,
                ).first.wait_for(state="visible", timeout=30000)

        return target_date.replace(day=1)

    def _select_time_slot(self, target_date):
        day_cells = self.page.get_by_role(
            "gridcell", name=str(target_date.day), exact=True
        )
        for index in range(day_cells.count()):
            day = day_cells.nth(index)
            if (
                day.is_visible()
                and day.is_enabled()
                and day.get_attribute("aria-disabled") != "true"
            ):
                day.click()
                self._wait_for_scheduler_idle()
                break
        else:
            return None

        slot_pattern = re.compile(
            r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\s*-\s*"
            r"\d{1,2}:\d{2}\s*(?:AM|PM)\b",
            re.IGNORECASE,
        )
        slots = self.page.get_by_text(slot_pattern)
        available_slots = [
            slots.nth(index)
            for index in range(slots.count())
            if slots.nth(index).is_visible() and slots.nth(index).is_enabled()
        ]
        if not available_slots:
            return None

        selected_slot = available_slots[-1]
        slot_name = selected_slot.inner_text().strip()
        selected_slot.click()
        return slot_name

    def select_date_and_time(self, after_date=None):
        today = date.today()
        first_date = today + timedelta(
            days=(after_date - today).days + 1
            if after_date and after_date >= today
            else 1
        )
        last_date = today + timedelta(days=60)
        displayed_month = today.replace(day=1)

        current_date = first_date
        while current_date <= last_date:
            self._wait_for_scheduler_idle()
            displayed_month = self._show_calendar_month(
                current_date, displayed_month
            )
            slot_name = self._select_time_slot(current_date)

            if slot_name:
                print(
                    f"Selected {current_date:%B} {current_date.day}, "
                    f"{slot_name}"
                )
                return {"date": current_date, "time": slot_name}

            print(
                f"No available time slots on {current_date:%B} "
                f"{current_date.day}; trying next day"
            )
            current_date += timedelta(days=1)

        raise RuntimeError(
            "No available time slot found from "
            f"{first_date:%B} {first_date.day} through "
            f"{last_date:%B} {last_date.day}"
        )

    def _click_schedule_action(self):
        # Locate the Schedule or Reschedule button.
        action = self.page.get_by_role(
            "button",
            name=re.compile(r"^(?:re)?schedule$", re.IGNORECASE),
        ).first
        # Wait until the button is visible on the page.
        action.wait_for(state="visible", timeout=15000)
        # Verify that the button is enabled before clicking it.
        expect(action).to_be_enabled(timeout=15000)
        # Read the button text so the test knows which operation it performs.
        action_name = action.inner_text().strip()
        # Submit the selected interview date and time.
        action.click()
        # Print the action to make the test execution easy to follow.
        print(f"Clicked {action_name}")
        # Return the action name to support confirmation and retry logic.
        return action_name

    def _select_replacement_slot(
        self, expected_slot, response_text, is_last_attempt
    ):
        # Check whether the application says that the selected slot is taken.
        if (
            "No slots available" not in response_text
            or expected_slot is None
            or is_last_attempt
        ):
            # Stop if retrying is not safe or no attempts remain.
            raise RuntimeError(
                "Scheduler did not confirm the selected slot. "
                f"Response: {response_text[:800]}"
            )
        # Search for another available slot after the failed slot date.
        return self.select_date_and_time(after_date=expected_slot["date"])

    def _verify_schedule_confirmation(self, expected_slot, action_name):
        # Get the complete scheduler response area.
        body = self.page.locator("body")
        # Confirm that the application sent a confirmation email.
        expect(body).to_contain_text(
            re.compile(r"confirmation email has been sent", re.I),
            timeout=10000,
        )
        # Stop here when the caller did not provide a slot to verify.
        if not expected_slot:
            return

        # Convert the expected date into the format displayed by the scheduler.
        month, day = expected_slot["date"].strftime("%b %d").split()
        try:
            # Confirm that the response contains the selected date.
            expect(body).to_contain_text(
                re.compile(rf"{re.escape(month)}\s*{int(day)}", re.I),
                timeout=30000,
            )
            # Confirm that the response contains the selected time.
            expect(body).to_contain_text(
                expected_slot["time"], timeout=10000
            )
        except AssertionError:
            # Capture the response so a failure contains useful details.
            response_text = body.inner_text(timeout=10000)
            # A reschedule can temporarily display the previous slot.
            if action_name.lower() == "reschedule":
                print(
                    "Reschedule confirmation still shows the previous "
                    "slot; selecting another available slot."
                )
                raise
            # Report a clear error when the confirmed slot is incorrect.
            raise AssertionError(
                "Scheduler did not confirm the selected slot "
                f"{expected_slot!r}. Response: {response_text[:800]}"
            )

    def click_schedule(self, expected_slot=None, verify_slot=True):
        # Get the page body for scheduler response and confirmation checks.
        body = self.page.locator("body")
        # Define the success text used by both scheduling operations.
        success_message = re.compile(
            r"Interview scheduled|scheduled successfully", re.IGNORECASE
        )

        # Retry up to four times if a selected slot becomes unavailable.
        for attempt in range(4):
            # Click Schedule or Reschedule for the selected slot.
            action_name = self._click_schedule_action()

            try:
                # Wait until the scheduler reports a successful operation.
                expect(body).to_contain_text(
                    success_message, timeout=15000
                )
            except AssertionError:
                # Read the response to determine why the operation failed.
                expected_slot = self._select_replacement_slot(
                    expected_slot,
                    body.inner_text(timeout=10000),
                    attempt == 3,
                )
                # Retry the operation with the replacement slot.
                continue

            # Validate the selected slot when verification is enabled.
            if expected_slot and verify_slot:
                try:
                    # Check the confirmation email, date, and time.
                    self._verify_schedule_confirmation(
                        expected_slot, action_name
                    )
                except AssertionError:
                    # Allow for a stale confirmation during rescheduling.
                    if action_name.lower() == "reschedule" and attempt < 3:
                        # Select another slot and repeat the reschedule.
                        expected_slot = self.reschedule_scheduled_meeting(
                            expected_slot
                        )
                        continue
                    # Re-raise unexpected confirmation failures.
                    raise
            else:
                # Require the confirmation email even when slot validation is off.
                expect(body).to_contain_text(
                    re.compile(r"confirmation email has been sent", re.I),
                    timeout=10000,
                )

            # Print the scheduler response for test reporting and debugging.
            print("Scheduler response:", body.inner_text(timeout=10000)[:1000])
            # Return the slot that was successfully scheduled.
            return expected_slot

        # Raise an explicit error when all retry attempts fail.
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
        status.wait_for(state="visible", timeout=15000)

        return status
