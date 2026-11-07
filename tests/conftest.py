
import sys
from pathlib import Path

import pytest

from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from utils.browser_factory import BrowserFactory
from utils.config_reader import ConfigReader
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


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


# Create Browser Context
@pytest.fixture(scope="function")
def browser_context(browser):

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
@pytest.fixture
def dashboard_page(page):
    return DashboardPage(page)


"""

pytest starts
    |
    v
playwright_instance()
    |
    v
browser()
    |
    v
browser_context()
    |
    v
page()
    |
    v
application() / login_page()
    |
    v
Execute Test Case
    |
    v
Teardown
    |
    v
Close Page
    |
    v
Close Context
    |
    v
Close Browser

"""