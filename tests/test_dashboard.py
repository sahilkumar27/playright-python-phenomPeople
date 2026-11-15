import pytest
from playwright.sync_api import expect

# Import environment and page-object configuration.
from utils.config_reader import ConfigReader
# Import page objects used by the dashboard workflow.
from pages.candidate_profile_page import CandidateProfilePage
from pages.dashboard_page import DashboardPage
from pages.interview_page import InterviewPage


@pytest.mark.e2e
class TestDashboard:

    #initial test setup to login and prepare the interview workflow
    def _prepare_interview_workflow(self, login_page, dashboard_page):
        # Store the candidate and job used by every interview scenario.
        candidate_name = "Pavan Chittala"
        job_title = "Hiring status automation run job"

        # Step 1: Open the CRM and authenticate the test user.
        print("\\nStep 1: Login to Phenom CRM")
        # Navigate to the configured application URL.
        login_page.open(ConfigReader.BASE_URL)
        # Enter credentials and complete the login flow.
        login_page.login(
            ConfigReader.USERNAME,
            ConfigReader.PASSWORD
        )

        # Confirm that login redirected to the CRM application.
        login_page.page.wait_for_url(
            lambda url: url.startswith(
                "https://uat-pipeline.phenompeople.com"
            ),
            timeout=30000
        )

        # Step 2: Search for the candidate in the dashboard.
        print("\\nStep 2: Search candidate")
        # Enter the candidate name into global search.
        dashboard_page.search_candidate(candidate_name)
        # Wait for and collect the search results.
        dashboard_page.get_search_results()

        # Step 3: Open the candidate profile in a new browser tab.
        print("\\nStep 3: Open candidate profile")
        # Capture the popup created by the external profile link.
        with login_page.page.expect_popup() as popup_info:
            # Click the candidate profile link.
            dashboard_page.open_candidate_profile()

        # Read the newly opened profile tab from the popup event.
        candidate_profile_tab = popup_info.value
        # Wait until the profile document has loaded.
        candidate_profile_tab.wait_for_load_state("domcontentloaded")

        # Step 4: Open the interview invitation form.
        print("\\nStep 4: Select interview invitation")
        # Create a page object for the candidate profile tab.
        candidate_profile_page = CandidateProfilePage(
            candidate_profile_tab
        )
        # Open the candidate's additional actions menu.
        candidate_profile_page.click_more_options()
        # Select the option to invite the candidate to an interview.
        candidate_profile_page.click_invite_to_job_interview()
        # Choose a single-meeting interview.
        candidate_profile_page.click_single_meeting()

        # Step 5: Configure and send the interview availability request.
        print("\\nStep 5: Create interview availability request")
        # We are creating an InterviewPage object and connecting it to the candidate profile browser tab.
        interview_page = InterviewPage(candidate_profile_tab)
        # Generate and enter a unique meeting title.
        meeting_title = interview_page.generate_meeting_title()

        # Search for and select the interviewer.
        interview_page.search_interviewer(
            "aarthi.mupparthy@phenom.com"
        )
        # Select the online meeting type.
        interview_page.click_meeting_type()
        # Select Google Meet as the communication channel.
        interview_page.select_meeting_channel()
        # Select the meeting duration and move to date configuration.
        interview_page.select_duration_and_continue()

        # Confirm that the scheduling-window option is displayed.
        expect(
            interview_page.schedule_within_option
        ).to_be_visible(timeout=30000)

        # Confirm that the application uses the expected 25-day window.
        expect(
            interview_page.schedule_within_days
        ).to_have_value("25")

        # Continue from date/time settings to communication settings.
        interview_page.verify_date_time_and_continue()
        # Disable unwanted notifications and send the invitation.
        interview_page.configure_communication_and_send_invite()

        # Step 6: Return to the dashboard and find the pending invitation.
        print("\\nStep 6: Find pending interview invitation")
        # Navigate back to the dashboard using the application link.
        interview_page.navigate_to_dashboard()
        # Bring the original profile tab to the foreground.
        candidate_profile_tab.bring_to_front()

        # Build the recruiter dashboard URL from the current host. Navigate to the parent tab
        dashboard_url = (
            candidate_profile_tab.url.split("/dashboard", 1)[0]
            + "/dashboard/recruiter-dashboard"
        )

        # Open the recruiter dashboard.
        candidate_profile_tab.goto(
            dashboard_url,
            wait_until="domcontentloaded"
        )

        # Create a dashboard page object for the profile tab.
        dashboard_page = DashboardPage(candidate_profile_tab)
        # Wait until pending and upcoming meeting tabs are available.
        dashboard_page.wait_for_meeting_tabs()
        # Scroll to the meeting section.
        dashboard_page.scroll_down(600)
        # Open the pending-meetings tab.
        dashboard_page.click_my_pending_tab()

        # Confirm that the newly created meeting is listed as pending.
        expect(
            dashboard_page.meeting_row(meeting_title)
        ).to_be_visible(timeout=30000)

        # Step 7: Verify the availability email.
        print("\\nStep 7: Verify availability email")
        # Open the meeting activity for the generated meeting.
        dashboard_page.open_meeting_by_title(meeting_title)
        # Open the meeting activity panel.
        dashboard_page.click_my_meetings_activity()
        # Open the email preview.
        dashboard_page.click_preview_conversion()
        # Verify the expected availability email subject.
        availability_subject = (
            f"Interview availability - {candidate_name} - {job_title}"
        )
        dashboard_page.verify_email_subject_starts_with(
            availability_subject
        )
        dashboard_page.verify_availability_email_details(
            availability_subject,
            meeting_title,
            duration="30 min",
        )


        # Step 8: Open the scheduling link from the email preview.
        print("\\nStep 8: Open scheduling link")
        # Open the scheduling link in a new page.
        scheduling_page = dashboard_page.click_meeting_link()
        # Create a dashboard page object for the scheduling page.
        scheduling_dashboard = DashboardPage(scheduling_page)

        # Open the pending request and prepare its calendar. (	Passes the job title to identify the correct job)
        scheduling_dashboard.open_pending_scheduling(meeting_title, job_title=job_title)

        # Return sends a value back from a function to wherever that function was called. (also called tuple unpacking)
        return (
            candidate_profile_tab,
            scheduling_dashboard,
            meeting_title,
            dashboard_url,
            candidate_name,
            job_title
        )

    def _verify_and_cancel_interview(
        self,
        candidate_profile_tab,
        scheduling_dashboard,
        meeting_title,
        dashboard_url,
        candidate_name,
        job_title,
        final_slot
    ):
        # Step 1: Return to the parent dashboard after scheduling.
        print("\\nReturning to dashboard")
        # Switch from the scheduling page back to the profile/dashboard tab.
        scheduling_dashboard.return_to_parent_tab(
            candidate_profile_tab
        )

        # Reload the recruiter dashboard to obtain current meeting data.
        candidate_profile_tab.goto(dashboard_url, wait_until="domcontentloaded")

        # Recreate the dashboard page object for the active tab.
        dashboard_page = DashboardPage(candidate_profile_tab)
        # Wait for the dashboard meeting tabs.
        dashboard_page.wait_for_meeting_tabs()
        # Scroll to the meeting list.
        dashboard_page.scroll_down(600)

        # Step 2: Verify the meeting in My Upcoming.
        print("\\nVerifying upcoming meeting")
        # Open the upcoming-meetings tab.
        dashboard_page.click_my_upcoming_tab()
        # Search all activities for the scheduled meeting.
        dashboard_page.open_all_meeting_activities(meeting_title)

        # Confirm the meeting date, time, and Upcoming status.
        dashboard_page.verify_meeting_in_upcoming(meeting_title, final_slot)

        # Step 3: Verify the confirmation email.
        print("\\nVerifying confirmation email")
        # Open the scheduled meeting activity.
        dashboard_page.open_meeting_activity(meeting_title)
        # Confirm the interview confirmation email subject.
        dashboard_page.verify_confirmation_email(candidate_name, job_title)

        # Step 4: Cancel the scheduled meeting.
        print("\\nCancelling the meeting")
        # Reload the dashboard so the cancellation controls are current.
        candidate_profile_tab.reload(wait_until="domcontentloaded")

        # Recreate the page object after reloading the tab.
        dashboard_page = DashboardPage(candidate_profile_tab)
        # Find the meeting to cancel.
        dashboard_page.open_all_meeting_activities(meeting_title)
        # Open the meeting action menu.
        dashboard_page.click_three_dot(meeting_title)
        # Select the cancel action.
        dashboard_page.click_cancel_meeting()
        # Select the required cancellation reason.
        dashboard_page.select_cancel_reason()
        # Confirm the cancellation.
        dashboard_page.click_yes_cancel_meeting()

        # Step 5: Verify the exact cancellation status.
        print("\\nVerifying cancellation status")
        # Reload so the status is read from the updated application state.
        candidate_profile_tab.reload(wait_until="domcontentloaded")

        # Recreate the page object after the reload.
        dashboard_page = DashboardPage(candidate_profile_tab)
        # Search all meetings, including canceled meetings.
        dashboard_page.open_all_meeting_activities(meeting_title, status="all")

        # Locate the status element for the generated meeting.
        cancelled_status = dashboard_page.get_meeting_status(meeting_title, expected_status="Cancelled")

        # Assert that the meeting is visibly marked as canceled.
        expect(cancelled_status).to_be_visible(timeout=30000)
        # Print a readable success message for the test report.
        print(f"PASS: Meeting '{meeting_title}' is Cancelled")

    # Test 1: Create, schedule, verify, and cancel an interview.
    def test_schedule_interview(self, login_page, dashboard_page):
        # Print a separator so this workflow is easy to identify in logs.
        print("\\n========== SCHEDULE INTERVIEW ==========")

        # Prepare the candidate and interview scheduling page. {tuple unpacking - to recieve multiple returned values into separate variables}
        (
            candidate_profile_tab,
            scheduling_dashboard,
            meeting_title,
            dashboard_url,
            candidate_name,
            job_title
        ) = self._prepare_interview_workflow( login_page,dashboard_page)

        # Select the first available future date and time.
        print("\\nSelecting interview date and time")
        scheduled_slot = (scheduling_dashboard.select_date_and_time())

        # Submit the selected interview slot.
        print("\\nScheduling interview")
        scheduled_slot = scheduling_dashboard.click_schedule(scheduled_slot)

        # Verify the scheduled interview and cancel it at the end.
        self._verify_and_cancel_interview(
            candidate_profile_tab,
            scheduling_dashboard,
            meeting_title,
            dashboard_url,
            candidate_name,
            job_title,
            scheduled_slot
        )

    # Test 2: Schedule, reschedule, verify, and cancel an interview.
    def test_reschedule_interview(self, login_page, dashboard_page):
        # Print a separator so this workflow is easy to identify in logs.
        print("\\n========== RESCHEDULE INTERVIEW ==========")

        # Prepare the candidate and interview scheduling page.
        (
            candidate_profile_tab,
            scheduling_dashboard,
            meeting_title,
            dashboard_url,
            candidate_name,
            job_title
        ) = self._prepare_interview_workflow(login_page,dashboard_page)

        # First schedule the original interview slot.
        print("\\nScheduling original interview")
        original_slot = (scheduling_dashboard.select_date_and_time())

        # Submit the original slot.
        original_slot = scheduling_dashboard.click_schedule(original_slot)

        # Open the reschedule flow and select a different slot.
        print("\\nRescheduling interview")
        new_slot = (scheduling_dashboard.reschedule_scheduled_meeting(original_slot))

        # Ensure rescheduling did not keep the original slot.
        assert new_slot != original_slot, ("Rescheduling must select a different time slot")

        # Submit the replacement slot.
        new_slot = scheduling_dashboard.click_schedule(new_slot)

        # Verify the rescheduled interview and cancel it at the end.
        self._verify_and_cancel_interview(
            candidate_profile_tab,
            scheduling_dashboard,
            meeting_title,
            dashboard_url,
            candidate_name,
            job_title,
            new_slot
        )
