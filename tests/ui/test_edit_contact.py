import re
import pytest
from playwright.sync_api import Page, expect

from application.crm.workflows.authentication_workflow import AuthenticationWorkflow
from application.crm.workflows.contact_workflow import ContactWorkflow
from framework.config.settings import Settings


@pytest.mark.regression
@pytest.mark.ui
def test_edit_contact(
    page: Page,
    settings: Settings,
    auth_workflow: AuthenticationWorkflow,
    contact_workflow: ContactWorkflow,
) -> None:
    """Create a contact, edit it with new data, verify the updated values are saved."""
    auth_workflow.login(settings.username, settings.password)
    contact_workflow.create(settings.contact)
    expect(page).to_have_url(re.compile(r"#/contacts/record/"))

    contact_workflow.edit(settings.contact_edit)
    expect(page).to_have_url(re.compile(r"#/contacts/record/"))
    contact_workflow.contact_page.verify(settings.contact_edit)
    #delete 
    contact_workflow.navigate_to_list()
    contact_workflow.bulk_delete_first_n(1)
    expect(page.locator("div.alert-success")).to_contain_text("Record(s) deleted successfully")
