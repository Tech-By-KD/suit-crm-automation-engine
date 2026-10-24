import pytest
from playwright.sync_api import Page, expect

from application.crm.workflows.authentication_workflow import AuthenticationWorkflow
from framework.config.settings import Settings


@pytest.mark.smoke
@pytest.mark.ui
def test_valid_credentials_land_on_home(
    page: Page, settings: Settings, auth_workflow: AuthenticationWorkflow
) -> None:

    auth_workflow.login(settings.username, settings.password)

    expect(page).to_have_url(settings.home_url)
