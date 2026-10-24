"""Typed, validated framework settings."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class _Strict(BaseModel):
    # Unknown keys (typos in YAML) must fail loudly instead of being ignored.
    model_config = ConfigDict(extra="forbid")


class Viewport(_Strict):
    width: int = Field(1440, gt=0)
    height: int = Field(900, gt=0)


class BrowserSettings(_Strict):
    name: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = True
    viewport: Viewport = Viewport()


class Timeouts(_Strict):
    default: int = Field(10_000, gt=0, description="ms")
    navigation: int = Field(30_000, gt=0, description="ms")


class ArtifactSettings(_Strict):
    screenshots: bool = True
    traces: bool = True


class ContactData(_Strict):
    salutation: str = ""
    first_name: str = ""
    last_name: str
    phone_work: str = ""
    phone_mobile: str = ""
    title: str = ""
    department: str = ""
    email: str = ""
    address_street: str = ""
    address_city: str = ""
    address_state: str = ""
    address_postalcode: str = ""
    address_country: str = ""


class Settings(_Strict):
    """Resolved configuration for one test run."""

    environment: str
    base_url: str
    username: str = Field(min_length=1)
    password: SecretStr
    browser: BrowserSettings = BrowserSettings()
    timeouts: Timeouts = Timeouts()
    artifacts: ArtifactSettings = ArtifactSettings()
    contact: ContactData = ContactData(last_name="")
    contact_edit: ContactData = ContactData(last_name="")

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return value.rstrip("/")

    @property
    def login_url(self) -> str:
        return f"{self.base_url}/#/Login"

    @property
    def home_url(self) -> str:
        return f"{self.base_url}/#/home"
