import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utils.config_reader import ConfigReader


@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {
        "channel": ConfigReader.BROWSER,
        "headless": ConfigReader.HEADLESS,
        "slow_mo": ConfigReader.SLOW_MO,
        "args": ["--start-maximized"],
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "no_viewport": True,
        "ignore_https_errors": True,
    }


@pytest.fixture(autouse=True)
def set_page_timeout(page: Page):
    page.set_default_timeout(ConfigReader.DEFAULT_TIMEOUT)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def dashboard_page(page: Page) -> DashboardPage:
    return DashboardPage(page)