
import sys
import json
from datetime import datetime
from pathlib import Path

import allure
import pytest
from playwright.sync_api import sync_playwright

# Project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Project imports
from utils.browser_factory import BrowserFactory
from utils.config_reader import ConfigReader
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


# Authentication state file
AUTH_FILE = ROOT_DIR / "auth" / "auth_state.json"


def _local_timestamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def pytest_configure(config):
    """Capture one local timestamp and report environment for this run."""
    config._allure_run_started_at = _local_timestamp()


def pytest_sessionfinish(session, exitstatus):
    """Write run metadata displayed in the Allure Environment section."""
    report_dir = session.config.getoption("--alluredir", default=None)
    if not report_dir:
        return

    destination = Path(report_dir)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "environment.properties").write_text(
        "Application=Phenom CRM UAT\n"
        "Test Suite=Interview Scheduling\n"
        f"Run Started At={session.config._allure_run_started_at}\n",
        encoding="utf-8",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach browser screenshots and URLs to failed Allure test results."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    context = item.funcargs.get("browser_context")
    if context is None:
        page = item.funcargs.get("page")
        contexts = [page.context] if page and not page.is_closed() else []
    else:
        contexts = [context]

    for context_index, browser_context in enumerate(contexts, start=1):
        for page_index, page in enumerate(browser_context.pages, start=1):
            if page.is_closed():
                continue
            prefix = f"Context {context_index} - Page {page_index}"
            allure.attach(
                page.url,
                name=f"{prefix} URL",
                attachment_type=allure.attachment_type.TEXT,
            )
            try:
                allure.attach(
                    page.screenshot(full_page=True),
                    name=f"{prefix} failure screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as error:
                allure.attach(
                    f"Could not capture failure screenshot: {error}",
                    name=f"{prefix} screenshot capture error",
                    attachment_type=allure.attachment_type.TEXT,
                )


# Initialize Playwright
@pytest.fixture(scope="session")
def playwright_instance():

    with sync_playwright() as playwright:
        yield playwright


# Launch Browser
@pytest.fixture(scope="session")
def browser(playwright_instance):

    browser = BrowserFactory.launch_browser(
        playwright_instance
    )

    yield browser

    browser.close()


# Force fresh login when required
@pytest.fixture
def force_login(request):

    return request.node.get_closest_marker("force_login") is not None


# Create Browser Context
@pytest.fixture(scope="function")
def browser_context(browser, force_login):

    AUTH_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Check whether a valid authentication file exists
    valid_auth_file = False

    if AUTH_FILE.exists() and AUTH_FILE.stat().st_size > 0:

        try:
            with AUTH_FILE.open("r", encoding="utf-8") as file:
                auth_data = json.load(file)

            if isinstance(auth_data, dict):
                valid_auth_file = True

        except (json.JSONDecodeError, OSError):
            print("Invalid authentication file. Creating fresh context.")

    # Load saved session unless fresh login is requested
    if valid_auth_file and not force_login:

        print("Loading previously saved login session")

        context = browser.new_context(
            storage_state=str(AUTH_FILE),
            no_viewport=True,
            ignore_https_errors=True
        )

    else:

        print("Creating fresh browser context")

        context = BrowserFactory.create_context(browser)

    yield context

    context.close()


# Create Browser Page
@pytest.fixture(scope="function")
def page(browser_context):

    page = browser_context.new_page()

    page.set_default_timeout(
        ConfigReader.DEFAULT_TIMEOUT
    )

    yield page

    page.close()


# Navigate to Phenom Application
@pytest.fixture(scope="function")
def application(page):

    page.goto(ConfigReader.BASE_URL)

    yield page


# Login Page Object Fixture
@pytest.fixture(scope="function")
def login_page(page):

    return LoginPage(page)


# Dashboard Page Object Fixture
@pytest.fixture(scope="function")
def dashboard_page(page):

    return DashboardPage(page)


# Save Authentication State
@pytest.fixture(scope="function")
def save_auth_state(browser_context):

    def save_session():

        AUTH_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        browser_context.storage_state(
            path=str(AUTH_FILE)
        )

        print("Login session saved successfully")

    return save_session


# Browser Context Execution Flow:
#
# pytest starts
#       |
#       v
# playwright_instance()
#       |
#       v
# browser()
#       |
#       v
# browser_context()
#       |
#       v
# Check authentication file
#       |
#       +---- Valid saved session?
#       |          |
#       |       Yes | No
#       |          |
#       v          v
# Load session   Fresh context
#       |          |
#       +-----+----+
#             |
#             v
#           page()
#             |
#             v
#         Execute test
#             |
#             v
#         Close page
#             |
#             v
#       Close context
#             |
#             v
#       Close browser
