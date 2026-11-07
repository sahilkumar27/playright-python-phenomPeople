from playwright.sync_api import Page


def current_url(page: Page) -> str:
    return page.url
