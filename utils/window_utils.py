from playwright.sync_api import Page


class WindowUtils:

    @staticmethod
    def get_all_pages(page: Page):

        return page.context.pages

    @staticmethod
    def get_new_tab(page: Page, action):

        with page.expect_popup() as popup_info:

            action()

        return popup_info.value

    @staticmethod
    def switch_to_latest_tab(page: Page):

        pages = page.context.pages

        if not pages:
            raise Exception("No browser tabs available")

        return pages[-1]

    @staticmethod
    def switch_to_tab_by_url(page: Page, url: str):

        for tab in page.context.pages:

            if url in tab.url:

                return tab

        raise Exception(f"Tab not found for URL: {url}")

    @staticmethod
    def close_current_tab(page: Page):

        page.close()