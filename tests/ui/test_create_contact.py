import re
import pytest
from playwright.sync_api import Page, expect

from application.crm.workflows.authentication_workflow import AuthenticationWorkflow
from application.crm.workflows.contact_workflow import ContactWorkflow
from framework.config.settings import Settings


@pytest.mark.regression
@pytest.mark.ui
def test_create_contact(
    page: Page,
    settings: Settings,
    auth_workflow: AuthenticationWorkflow,
    contact_workflow: ContactWorkflow,
) -> None:
    """Log in, navigate to Create Contact via the nav menu, fill the form and save."""
    auth_workflow.login(settings.username, settings.password)
    contact_workflow.create(settings.contact)
    expect(page).to_have_url(re.compile(r"#/contacts/record/"))
    contact_workflow.contact_page.verify(settings.contact)
