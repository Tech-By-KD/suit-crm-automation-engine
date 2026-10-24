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


class Settings(_Strict):
    """Resolved configuration for one test run."""

    environment: str
    base_url: str
    username: str = Field(min_length=1)
    password: SecretStr
    browser: BrowserSettings = BrowserSettings()
    timeouts: Timeouts = Timeouts()
    artifacts: ArtifactSettings = ArtifactSettings()

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
