
import pytest

from utils.config_reader import ConfigReader
from pages.candidate_profile_page import CandidateProfilePage
from pages.interview_page import InterviewPage
from pages.dashboard_page import DashboardPage
from playwright.sync_api import expect

@pytest.mark.e2e
class TestDashboard:

    @pytest.mark.parametrize(
        "should_reschedule", [False, True], ids=["scheduled", "rescheduled"]
    )
    def test_search_candidate(
        self, login_page, dashboard_page, should_reschedule
    ):
        candidate_name = "Pavan Chittala"
        job_title = "Hiring status automation run job"

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

        # Step 3: Search Candidate
        dashboard_page.search_candidate(candidate_name)

        print("Searching for Pavan Chittala")

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
        candidate_profile_page = CandidateProfilePage(
            candidate_profile_tab
        )

        # Step 7: Click Three-Dot Menu
        candidate_profile_page.click_more_options()

        # Step 8: Select Invite to Job Interview
        candidate_profile_page.click_invite_to_job_interview()

        print("Invite to Job Interview selected")

        # Step 9: Select Single Meeting
        candidate_profile_page.click_single_meeting()

        print("Single Meeting selected successfully")

        # Step 10: Initialize Interview Page
        interview_page = InterviewPage(candidate_profile_tab)

        # Step 11: Generate and Enter Meeting Title
        meeting_title = interview_page.generate_meeting_title()

        print("Generated Meeting Title:", meeting_title)

        # Step 12: Search Interviewer
        interview_page.search_interviewer(
            "aarthi.mupparthy@phenom.com"
        )

        print("Interviewer search submitted")

        # Step 13: Click Meeting Type
        interview_page.click_meeting_type()

        # Step 14: Select Channel
        interview_page.select_meeting_channel()

        #Step 15: Select Duration and click next
        interview_page.select_duration_and_continue()

        # Step 16: Verify the default schedule window
        expect(
            interview_page.schedule_within_option
        ).to_be_visible()
        expect(
            interview_page.schedule_within_days
        ).to_have_value("25")

        print("PASS: Schedule within defaults to 25 business days")

        # Continue to Communication page
        interview_page.verify_date_time_and_continue()

        # Step 17: Configure Communication and Send Invite
        interview_page.configure_communication_and_send_invite()


        #Step 19: Navigate back to the dashboard and verify that the interview invite is visible in the upcoming interviews section

        interview_page.navigate_to_dashboard()
        candidate_profile_tab.bring_to_front()
        dashboard_page = DashboardPage(candidate_profile_tab)
        dashboard_url = (
            candidate_profile_tab.url.split("/dashboard", 1)[0]
            + "/dashboard/recruiter-dashboard"
        )
        candidate_profile_tab.goto(
            dashboard_url, wait_until="domcontentloaded"
        )

        dashboard_page.wait_for_meeting_tabs()
        dashboard_page.scroll_down(600)
        dashboard_page.click_my_pending_tab()
        expect(dashboard_page.meeting_row(meeting_title)).to_be_visible(
            timeout=30000
        )
        dashboard_page.open_meeting_by_title(meeting_title)


        dashboard_page.click_my_meetings_activity()
        dashboard_page.click_preview_conversion()
        dashboard_page.verify_email_subject(
            f"Interview availability - {candidate_name} - {job_title}"
        )

        # Step 22: Scroll inside Preview Conversation
        dashboard_page.scroll_preview_conversation(500)

        # Step 23: Click scheduling link and capture new tab
        scheduling_page = dashboard_page.click_meeting_link()
        scheduling_dashboard = DashboardPage(scheduling_page)
        scheduling_dashboard.open_pending_scheduling(meeting_title)
        scheduled_slot = scheduling_dashboard.select_date_and_time()
        scheduled_slot = scheduling_dashboard.click_schedule(scheduled_slot)

        verified_slot = scheduled_slot
        if should_reschedule:
            verified_slot = (
                scheduling_dashboard.reschedule_scheduled_meeting(
                    scheduled_slot
                )
            )
            assert verified_slot != scheduled_slot, (
                "Rescheduling must select a different time slot"
            )
            verified_slot = scheduling_dashboard.click_schedule(
                verified_slot, verify_slot=False
            )

        scheduling_dashboard.return_to_parent_tab(candidate_profile_tab)
        candidate_profile_tab.goto(
            dashboard_url, wait_until="domcontentloaded"
        )
        dashboard_page.wait_for_meeting_tabs()
        dashboard_page.scroll_down(600)

        print("Dashboard interview scheduling flow completed")

        # Verify the scheduled meeting and its slot under My Upcoming.
        dashboard_page.click_my_upcoming_tab()
        dashboard_page.open_all_meeting_activities(meeting_title)
        dashboard_page.verify_meeting_in_upcoming(
            meeting_title, verified_slot
        )
        dashboard_page.open_meeting_activity(meeting_title)
        dashboard_page.verify_confirmation_email(candidate_name, job_title)

        # Reload the full activity table to dismiss the conversation panel.
        candidate_profile_tab.reload(wait_until="domcontentloaded")
        dashboard_page = DashboardPage(candidate_profile_tab)
        dashboard_page.open_all_meeting_activities(meeting_title)

        # Step 24: Cancel the scheduled meeting
        dashboard_page.click_three_dot(meeting_title)
        dashboard_page.click_cancel_meeting()
        dashboard_page.select_cancel_reason()
        dashboard_page.click_yes_cancel_meeting()

        # Step 25: Refresh dashboard
        candidate_profile_tab.reload(wait_until="domcontentloaded")

        # Reload the all-activity view and find this meeting's status.
        dashboard_page.open_all_meeting_activities(
            meeting_title, status="all"
        )

        # Step 26: Verify meeting cancellation status [Status Update ASSERTION]
        cancelled_status = dashboard_page.get_meeting_status(
            meeting_title
        )

        expect(cancelled_status).to_be_visible()

        print(
            f"PASS: Meeting '{meeting_title}' status is Cancelled"
        )
