import pytest
from playwright.sync_api import Page, expect

from application.crm.workflows.authentication_workflow import AuthenticationWorkflow
from application.crm.workflows.contact_workflow import ContactWorkflow
from framework.config.settings import Settings


@pytest.mark.regression
@pytest.mark.ui
def test_delete_contacts_bulk(
    page: Page,
    settings: Settings,
    auth_workflow: AuthenticationWorkflow,
    contact_workflow: ContactWorkflow,
) -> None:
    auth_workflow.login(settings.username, settings.password)
    contact_workflow.navigate_to_list()
    contact_workflow.bulk_delete_first_n(1)
    expect(page.locator("div.alert-success")).to_contain_text("Record(s) deleted successfully")
