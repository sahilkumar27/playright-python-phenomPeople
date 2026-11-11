
from datetime import datetime

import allure
import pytest

from utils.config_reader import ConfigReader
from pages.candidate_profile_page import CandidateProfilePage
from pages.interview_page import InterviewPage
from pages.dashboard_page import DashboardPage
from playwright.sync_api import expect

@allure.epic("Phenom CRM Automation")
@allure.feature("Interview scheduling")
@allure.story("Schedule and reschedule candidate interviews")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.e2e
@pytest.mark.force_login
class TestDashboard:

    @pytest.mark.parametrize(
        "should_reschedule", [False, True], ids=["scheduled", "rescheduled"]
    )
    def test_search_candidate(
        self, login_page, dashboard_page, should_reschedule
    ):
        run_started_at = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
        scenario = (
            "Rescheduled interview"
            if should_reschedule
            else "Scheduled interview"
        )
        allure.dynamic.title(
            f"{scenario} - candidate availability workflow ({run_started_at})"
        )
        allure.dynamic.suite("Candidate Interview Workflows")
        allure.dynamic.sub_suite(scenario)
        allure.dynamic.description(
            "Creates an interview availability request, schedules the meeting, "
            "verifies its email and final CRM status, then cancels it."
        )
        allure.dynamic.parameter("Run started at", run_started_at)
        allure.dynamic.tag("dashboard", "end-to-end")
        allure.attach(
            f"Scenario: {scenario}\nRun started at: {run_started_at}",
            name="Run details",
            attachment_type=allure.attachment_type.TEXT,
        )

        candidate_name = "Pavan Chittala"
        # The candidate profile used by this UAT account is associated with
        # Technical Lead; that is the job name emitted in CRM email subjects.
        job_title = "Technical Lead"

        with allure.step("Log in and open the candidate profile"):
            login_page.open(ConfigReader.BASE_URL)
            login_page.login(ConfigReader.USERNAME, ConfigReader.PASSWORD)
            login_page.page.wait_for_url(
                lambda url: url.startswith(
                    "https://uat-pipeline.phenompeople.com"
                ),
                timeout=30000,
            )

            dashboard_page.search_candidate(candidate_name)
            dashboard_page.get_search_results()

            with login_page.page.expect_popup() as popup_info:
                dashboard_page.open_candidate_profile()

            candidate_profile_tab = popup_info.value
            candidate_profile_tab.wait_for_load_state("domcontentloaded")
            candidate_profile_page = CandidateProfilePage(
                candidate_profile_tab
            )
            candidate_profile_page.click_more_options()
            candidate_profile_page.click_invite_to_job_interview()
            candidate_profile_page.click_single_meeting()

        print("Successfully navigated to Dashboard")
        print("Searching for Pavan Chittala")
        print("First candidate selected successfully")
        print("Candidate profile opened successfully")
        print("Candidate Profile URL:", candidate_profile_tab.url)
        print("Invite to Job Interview selected")
        print("Single Meeting selected successfully")

        interview_page = InterviewPage(candidate_profile_tab)

        meeting_title = interview_page.generate_meeting_title()
        print("Generated Meeting Title:", meeting_title)

        with allure.step(
            "Create and send the interview availability request"
        ):
            interview_page.search_interviewer(
                "aarthi.mupparthy@phenom.com"
            )
            interview_page.click_meeting_type()
            interview_page.select_meeting_channel()
            interview_page.select_duration_and_continue()
            expect(
                interview_page.schedule_within_option
            ).to_be_visible()
            expect(interview_page.schedule_within_days).to_have_value("25")
            interview_page.verify_date_time_and_continue()
            interview_page.configure_communication_and_send_invite()


        # Step 19: Return to the dashboard and verify the pending invite.

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
        with allure.step("Verify the availability email preview"):
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
        scheduling_dashboard.open_pending_scheduling(
            meeting_title, job_title=job_title
        )
        with allure.step("Schedule the interview"):
            scheduled_slot = scheduling_dashboard.select_date_and_time()
            scheduled_slot = scheduling_dashboard.click_schedule(
                scheduled_slot
            )

        verified_slot = scheduled_slot
        if should_reschedule:
            with allure.step("Reschedule the interview to a different slot"):
                verified_slot = (
                    scheduling_dashboard.reschedule_scheduled_meeting(
                        scheduled_slot
                    )
                )
                assert verified_slot != scheduled_slot, (
                    "Rescheduling must select a different time slot"
                )
                verified_slot = scheduling_dashboard.click_schedule(
                    verified_slot
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
        with allure.step(
            "Verify the final meeting slot and confirmation email"
        ):
            dashboard_page.open_all_meeting_activities(meeting_title)
            dashboard_page.verify_meeting_in_upcoming(
                meeting_title, verified_slot
            )
            dashboard_page.open_meeting_activity(meeting_title)
            dashboard_page.verify_confirmation_email(
                candidate_name, job_title
            )

        # Reload the full activity table to dismiss the conversation panel.
        candidate_profile_tab.reload(wait_until="domcontentloaded")
        dashboard_page = DashboardPage(candidate_profile_tab)
        dashboard_page.open_all_meeting_activities(meeting_title)

        # Step 24: Cancel the scheduled meeting
        with allure.step("Cancel the meeting and verify its final status"):
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
