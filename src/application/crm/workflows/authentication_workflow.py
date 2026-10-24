"""Business workflow: authenticate against the CRM."""

from __future__ import annotations

from pydantic import SecretStr

from application.crm.pages.home_page import HomePage
from application.crm.pages.login_page import LoginPage


class AuthenticationWorkflow:
    def __init__(self, login_page: LoginPage, home_page: HomePage) -> None:
        self._login_page = login_page
        self._home_page = home_page

    def login(self, username: str, password: SecretStr) -> None:
        """Log in and verify the authenticated state (redirect to the home route)."""
        self._login_page.open()
        self._login_page.submit_credentials(username, password.get_secret_value())
        self._home_page.expect_loaded()
