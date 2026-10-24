"""Fixtures. Lifetimes:

- playwright / browser: session scope (per xdist worker process). Starting a browser is
  expensive and a browser holds no application state.
- context / page: function scope. A fresh context per test gives isolated cookies and
  storage, so tests never share authentication or application state.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, expect, sync_playwright

from application.crm.pages.home_page import HomePage
from application.crm.pages.login_page import LoginPage
from application.crm.workflows.authentication_workflow import AuthenticationWorkflow
from framework.config.loader import ConfigError, load_settings
from framework.config.settings import Settings
from framework.reporting.artifact_manager import ArtifactManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_REPORT_KEY = pytest.StashKey[dict]()


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("crm")
    group.addoption("--environment", default="test", help="config/environments/<name>.yaml")
    group.addoption("--browser", default=None, choices=["chromium", "firefox", "webkit"])
    group.addoption("--headed", action="store_true", help="Run the browser with a visible UI")
    group.addoption("--base-url", default=None, help="Override the CRM base URL")


@pytest.fixture(scope="session")
def settings(pytestconfig: pytest.Config) -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")  # does not override variables already set (CI secrets)
    overrides: dict = {}
    if pytestconfig.getoption("--browser"):
        overrides.setdefault("browser", {})["name"] = pytestconfig.getoption("--browser")
    if pytestconfig.getoption("--headed"):
        overrides.setdefault("browser", {})["headless"] = False
    if pytestconfig.getoption("--base-url"):
        overrides["base_url"] = pytestconfig.getoption("--base-url")
    try:
        return load_settings(
            pytestconfig.getoption("--environment"), PROJECT_ROOT / "config", os.environ, overrides
        )
    except ConfigError as exc:
        # A setup problem, reported as an error rather than a test failure.
        pytest.exit(f"Configuration error: {exc}", returncode=3)


@pytest.fixture(scope="session")
def run_id() -> str:
    # xdist gives all workers the same testrun uid; fall back to a timestamp otherwise.
    return os.environ.get("PYTEST_XDIST_TESTRUNUID") or (
        f"{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    )


@pytest.fixture(scope="session")
def artifact_manager(run_id: str) -> ArtifactManager:
    return ArtifactManager(PROJECT_ROOT / "artifacts", run_id)


@pytest.fixture(scope="session")
def playwright_instance() -> Iterator[Playwright]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, settings: Settings) -> Iterator[Browser]:
    expect.set_options(timeout=settings.timeouts.default)
    launcher = getattr(playwright_instance, settings.browser.name)
    instance = launcher.launch(headless=settings.browser.headless)
    yield instance
    instance.close()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    report = yield
    item.stash.setdefault(_REPORT_KEY, {})[report.when] = report
    return report


@pytest.fixture
def context(
    browser: Browser,
    settings: Settings,
    request: pytest.FixtureRequest,
    artifact_manager: ArtifactManager,
) -> Iterator[BrowserContext]:
    ctx = browser.new_context(
        viewport={
            "width": settings.browser.viewport.width,
            "height": settings.browser.viewport.height,
        },
    )
    ctx.set_default_timeout(settings.timeouts.default)
    ctx.set_default_navigation_timeout(settings.timeouts.navigation)
    if settings.artifacts.traces:
        ctx.tracing.start(screenshots=True, snapshots=True, sources=False)

    yield ctx

    # Teardown: evidence must be saved BEFORE the context is closed.
    reports = request.node.stash.get(_REPORT_KEY, {})
    failed = any(r.failed for r in reports.values())
    out_dir = artifact_manager.test_dir(request.node.nodeid) if failed else None
    if settings.artifacts.traces:
        ctx.tracing.stop(path=str(out_dir / "trace.zip") if out_dir else None)
    if out_dir and settings.artifacts.screenshots:
        for index, page in enumerate(ctx.pages):
            page.screenshot(path=str(out_dir / f"screenshot-{index}.png"))
        (out_dir / "failure.txt").write_text(
            f"node_id: {request.node.nodeid}\nurls: {[p.url for p in ctx.pages]}\n",
            encoding="utf-8",
        )
    ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    return context.new_page()


@pytest.fixture
def login_page(page: Page, settings: Settings) -> LoginPage:
    return LoginPage(page, settings.login_url)


@pytest.fixture
def home_page(page: Page, settings: Settings) -> HomePage:
    return HomePage(page, settings.home_url)


@pytest.fixture
def auth_workflow(login_page: LoginPage, home_page: HomePage) -> AuthenticationWorkflow:
    return AuthenticationWorkflow(login_page, home_page)
