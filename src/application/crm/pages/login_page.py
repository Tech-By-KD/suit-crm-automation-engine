"""SuiteCRM 8 login page. Locators come from the real login form markup."""

from __future__ import annotations

from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page, login_url: str) -> None:
        self._page = page
        self._login_url = login_url
        # The inputs carry aria-labels ("Username"/"Password"); the button has id=login-button.
        self._username = page.get_by_label("Username")
        self._password = page.get_by_label("Password")
        self._submit = page.get_by_role("button", name="Log In")

    def open(self) -> None:
        """Navigate to the login page and wait until the form is usable."""
        self._page.goto(self._login_url)
        self._page.locator("app-loading").wait_for(state="detached")
        expect(self._username).to_be_visible()

    def submit_credentials(self, username: str, password: str) -> None:
        self._username.fill(username)
        self._password.fill(password)
        expect(self._submit).to_be_enabled()
        self._submit.click()
