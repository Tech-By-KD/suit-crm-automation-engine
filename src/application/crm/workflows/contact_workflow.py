"""Business workflow: create a contact via the nav menu."""

from __future__ import annotations
import re

from playwright.sync_api import Page, expect

from application.crm.pages.contact_page import ContactPage
from framework.config.settings import ContactData


class ContactWorkflow:
    def __init__(self, page: Page, contact_page: ContactPage) -> None:
        self._page = page
        self.contact_page = contact_page

    def navigate_to_list(self) -> None:
        """Navigate to the Contacts list view via the nav menu."""
        contacts_nav = self._page.locator(
            "scrm-base-menu-item-link a.top-nav-link", has_text="Contacts"
        ).first
        contacts_nav.hover()
        self._page.locator("a.sub-nav-link[href*='/contacts/index']").click()
        self._page.locator("tbody.ng-star-inserted tr.cdk-row").first.wait_for()

    def bulk_delete_first_n(self, n: int) -> None:
        """Check the first n rows and delete them via Bulk Action."""
        rows = self._page.locator("tbody tr.cdk-row")
        for i in range(n):
            row = rows.nth(i)
            row.locator("td.cdk-column-checkbox input[type='checkbox']").dispatch_event("click")
        self._page.locator(
            "scrm-table-header scrm-dropdown-button.d-none.d-sm-block button.bulk-action-button"
        ).click()
        self._page.locator("scrm-table-header scrm-dropdown-button.d-none.d-sm-block .dropdown-menu.show a.delete-bulk-action").click()
        self._page.locator("scrm-message-modal button.btn-main").wait_for()
        self._page.locator("scrm-message-modal button.btn-main").click()

    def open_first_from_list(self) -> None:
        """Navigate to the Contacts list via the nav menu and open the first contact."""
        contacts_nav = self._page.locator(
            "scrm-base-menu-item-link a.top-nav-link", has_text="Contacts"
        ).first
        contacts_nav.hover()
        self._page.locator("a.sub-nav-link[href*='/contacts/index']").click()
        self._page.locator("td.cdk-column-name a.field-link").first.click()
        expect(self._page).to_have_url(re.compile(r"#/contacts/record/"))

    def open_create_form(self) -> None:
        """Hover the Contacts nav item and click Create Contact from the dropdown."""
        contacts_nav = self._page.locator(
            "scrm-base-menu-item-link a.top-nav-link", has_text="Contacts"
        ).first
        contacts_nav.hover()
        self._page.locator(
            "a.sub-nav-link[href*='/contacts/edit']"
        ).click()
        self.contact_page.expect_loaded()

    def create(self, data: ContactData) -> None:
        self.open_create_form()
        self.contact_page.fill(data)
        self.contact_page.save()

    def edit(self, data: ContactData) -> None:
        self.contact_page.click_edit()
        self.contact_page.edit(data)
        self.contact_page.save()
