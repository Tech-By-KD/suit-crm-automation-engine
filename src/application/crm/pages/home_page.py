"""SuiteCRM 8 home page (landing page after authentication)."""

from __future__ import annotations

from playwright.sync_api import Page, expect


class HomePage:
    def __init__(self, page: Page, home_url: str) -> None:
        self._page = page
        self._home_url = home_url

    def expect_loaded(self) -> None:
        """Page contract: authenticated users land on the #/home route."""
        expect(self._page).to_have_url(self._home_url)
