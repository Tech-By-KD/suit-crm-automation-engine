"""Load settings from YAML files, environment variables and explicit overrides.

Precedence (lowest to highest):
    1. Built-in defaults (pydantic model defaults)
    2. config/config.yaml
    3. config/environments/<environment>.yaml
    4. Environment variables (CRM_*)
    5. Explicit overrides (pytest command-line options)
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from framework.config.settings import Settings

# Environment variable -> path inside the settings dict.
ENV_VAR_MAP: dict[str, tuple[str, ...]] = {
    "CRM_BASE_URL": ("base_url",),
    "CRM_USERNAME": ("username",),
    "CRM_PASSWORD": ("password",),
    "CRM_BROWSER": ("browser", "name"),
    "CRM_HEADLESS": ("browser", "headless"),
}

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


class ConfigError(Exception):
    """Raised when configuration is missing, malformed or invalid."""


def _read_yaml(path: Path, *, required: bool) -> dict[str, Any]:
    if not path.is_file():
        if required:
            raise ConfigError(f"Required config file not found: {path}")
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Malformed YAML in {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"Top level of {path} must be a mapping")
    return data


def _deep_merge(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _set_path(target: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    for key in path[:-1]:
        target = target.setdefault(key, {})
    target[path[-1]] = value


def _parse_bool(name: str, raw: str) -> bool:
    lowered = raw.strip().lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    raise ConfigError(f"{name} must be a boolean (true/false), got {raw!r}")


def _env_overrides(env: Mapping[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for var, path in ENV_VAR_MAP.items():
        raw = env.get(var)
        if raw is None or raw == "":
            continue
        value: Any = _parse_bool(var, raw) if var == "CRM_HEADLESS" else raw
        _set_path(result, path, value)
    return result


def load_settings(
    environment: str,
    config_dir: Path,
    env: Mapping[str, str],
    overrides: Mapping[str, Any] | None = None,
) -> Settings:
    """Build validated Settings, failing fast with a secret-safe message."""
    merged: dict[str, Any] = {}
    merged = _deep_merge(merged, _read_yaml(config_dir / "config.yaml", required=True))
    merged = _deep_merge(
        merged, _read_yaml(config_dir / "environments" / f"{environment}.yaml", required=True)
    )
    merged = _deep_merge(merged, _env_overrides(env))
    if overrides:
        merged = _deep_merge(merged, overrides)
    merged["environment"] = environment

    try:
        return Settings(**merged)
    except ValidationError as exc:
        # Report only field locations and messages; never echo input values (may be secrets).
        problems = "; ".join(
            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()
        )
        raise ConfigError(f"Invalid configuration: {problems}") from None
