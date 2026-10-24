"""SuiteCRM 8 create-contact page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.config.settings import ContactData


class ContactPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._create_url = f"{base_url}/#/contacts/edit?return_module=Contacts&return_action=DetailView"

    def expect_loaded(self) -> None:
        expect(self._page).to_have_url(self._create_url)

    def fill(self, data: ContactData) -> None:
        form = self._page.locator("scrm-field-layout form.create")
        form.wait_for()

        if data.salutation:
            form.locator(".dynamic-field-name-salutation select").select_option(data.salutation)
        if data.first_name:
            form.locator(".dynamic-field-name-first_name input").fill(data.first_name)
        form.locator(".dynamic-field-name-last_name input").fill(data.last_name)
        if data.phone_work:
            form.locator(".dynamic-field-name-phone_work input").fill(data.phone_work)
        if data.phone_mobile:
            form.locator(".dynamic-field-name-phone_mobile input").fill(data.phone_mobile)
        if data.title:
            form.locator(".dynamic-field-name-title input").fill(data.title)
        if data.department:
            form.locator(".dynamic-field-name-department input").fill(data.department)
        if data.email:
            form.locator(".dynamic-field-name-email_address input").fill(data.email)
        if data.address_street:
            form.locator(".dynamic-field-name-primary_address_street textarea").fill(data.address_street)
        if data.address_city:
            form.locator(".dynamic-field-name-primary_address_city input").fill(data.address_city)
        if data.address_state:
            form.locator(".dynamic-field-name-primary_address_state input").fill(data.address_state)
        if data.address_postalcode:
            form.locator(".dynamic-field-name-primary_address_postalcode input").fill(data.address_postalcode)
        if data.address_country:
            form.locator(".dynamic-field-name-primary_address_country input").fill(data.address_country)

    def save(self) -> None:
        self._page.locator("button.button-group-button.settings-button", has_text="Save").click()

    def click_edit(self) -> None:
        self._page.locator("button.button-group-button.settings-button", has_text="Edit").click()

    def edit(self, data: ContactData) -> None:
        form = self._page.locator("scrm-field-layout form.edit")
        form.wait_for()

        if data.salutation:
            form.locator(".dynamic-field-name-salutation select").select_option(data.salutation)
        if data.first_name:
            form.locator(".dynamic-field-name-first_name input").fill(data.first_name)
        if data.last_name:
            form.locator(".dynamic-field-name-last_name input").fill(data.last_name)
        if data.phone_work:
            form.locator(".dynamic-field-name-phone_work input").fill(data.phone_work)
        if data.phone_mobile:
            form.locator(".dynamic-field-name-phone_mobile input").fill(data.phone_mobile)
        if data.title:
            form.locator(".dynamic-field-name-title input").fill(data.title)
        if data.department:
            form.locator(".dynamic-field-name-department input").fill(data.department)
        if data.email:
            form.locator(".dynamic-field-name-email_address input").fill(data.email)
        if data.address_street:
            form.locator(".dynamic-field-name-primary_address_street textarea").fill(data.address_street)
        if data.address_city:
            form.locator(".dynamic-field-name-primary_address_city input").fill(data.address_city)
        if data.address_state:
            form.locator(".dynamic-field-name-primary_address_state input").fill(data.address_state)
        if data.address_postalcode:
            form.locator(".dynamic-field-name-primary_address_postalcode input").fill(data.address_postalcode)
        if data.address_country:
            form.locator(".dynamic-field-name-primary_address_country input").fill(data.address_country)

    def verify(self, data: ContactData) -> None:
        """Assert saved values on the detail view match what was submitted."""
        detail = self._page.locator("scrm-field-layout form.detail")
        detail.wait_for()

        def field(name: str) -> str:
            return detail.locator(f".dynamic-field-name-{name}").inner_text().strip()

        if data.salutation:
            expect(detail.locator(".dynamic-field-name-salutation scrm-dropdownenum-detail")).to_contain_text(data.salutation)
        if data.first_name:
            expect(detail.locator(".dynamic-field-name-first_name scrm-varchar-detail")).to_contain_text(data.first_name)
        expect(detail.locator(".dynamic-field-name-last_name scrm-varchar-detail")).to_contain_text(data.last_name)
        if data.phone_work:
            expect(detail.locator(".dynamic-field-name-phone_work scrm-phone-detail")).to_contain_text(data.phone_work)
        if data.phone_mobile:
            expect(detail.locator(".dynamic-field-name-phone_mobile scrm-phone-detail")).to_contain_text(data.phone_mobile)
        if data.title:
            expect(detail.locator(".dynamic-field-name-title scrm-varchar-detail")).to_contain_text(data.title)
        if data.department:
            expect(detail.locator(".dynamic-field-name-department scrm-varchar-detail")).to_contain_text(data.department)
        if data.email:
            expect(detail.locator(".dynamic-field-name-email_address scrm-email-detail")).to_contain_text(data.email)
        if data.address_street:
            expect(detail.locator(".dynamic-field-name-primary_address_street scrm-text-detail")).to_contain_text(data.address_street)
        if data.address_city:
            expect(detail.locator(".dynamic-field-name-primary_address_city scrm-varchar-detail")).to_contain_text(data.address_city)
        if data.address_state:
            expect(detail.locator(".dynamic-field-name-primary_address_state scrm-varchar-detail")).to_contain_text(data.address_state)
        if data.address_postalcode:
            expect(detail.locator(".dynamic-field-name-primary_address_postalcode scrm-varchar-detail")).to_contain_text(data.address_postalcode)
        if data.address_country:
            expect(detail.locator(".dynamic-field-name-primary_address_country scrm-varchar-detail")).to_contain_text(data.address_country)
