from pathlib import Path

import pytest

from framework.config.loader import ConfigError, load_settings
from framework.reporting.artifact_manager import safe_name

pytestmark = pytest.mark.unit

CREDS = {"CRM_USERNAME": "u", "CRM_PASSWORD": "s3cret-pw"}


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    (tmp_path / "environments").mkdir()
    (tmp_path / "config.yaml").write_text("browser:\n  headless: true\n", encoding="utf-8")
    (tmp_path / "environments" / "test.yaml").write_text(
        "base_url: https://yaml.example.com/\n", encoding="utf-8"
    )
    return tmp_path


def test_yaml_values_and_defaults_are_loaded(config_dir: Path) -> None:
    settings = load_settings("test", config_dir, CREDS)
    assert settings.base_url == "https://yaml.example.com"
    assert settings.browser.name == "chromium"
    assert settings.home_url == "https://yaml.example.com/#/home"


def test_precedence_env_beats_yaml_and_overrides_beat_env(config_dir: Path) -> None:
    env = {**CREDS, "CRM_BASE_URL": "https://env.example.com", "CRM_HEADLESS": "false"}
    settings = load_settings("test", config_dir, env)
    assert settings.base_url == "https://env.example.com"
    assert settings.browser.headless is False

    overridden = load_settings("test", config_dir, env, {"base_url": "https://cli.example.com"})
    assert overridden.base_url == "https://cli.example.com"


def test_missing_credentials_fail_fast(config_dir: Path) -> None:
    with pytest.raises(ConfigError, match="username"):
        load_settings("test", config_dir, {})


def test_error_message_does_not_leak_password(config_dir: Path) -> None:
    env = {**CREDS, "CRM_BASE_URL": "not-a-url"}
    with pytest.raises(ConfigError) as exc_info:
        load_settings("test", config_dir, env)
    assert "s3cret-pw" not in str(exc_info.value)


def test_malformed_yaml_is_reported(config_dir: Path) -> None:
    (config_dir / "config.yaml").write_text("browser: [unclosed", encoding="utf-8")
    with pytest.raises(ConfigError, match="Malformed YAML"):
        load_settings("test", config_dir, CREDS)


def test_unknown_yaml_key_is_rejected(config_dir: Path) -> None:
    (config_dir / "config.yaml").write_text("browzer: {}\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="browzer"):
        load_settings("test", config_dir, CREDS)


def test_safe_name_makes_node_ids_filesystem_safe() -> None:
    name = safe_name("tests/ui/test_login.py::test_valid[param with spaces]")
    assert "/" not in name and ":" not in name and " " not in name
