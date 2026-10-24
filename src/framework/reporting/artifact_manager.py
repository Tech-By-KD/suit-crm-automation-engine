"""Predictable, collision-free locations for per-test failure artifacts."""

from __future__ import annotations

import re
from pathlib import Path

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")
_MAX_LEN = 120


def safe_name(node_id: str) -> str:
    """Turn a pytest node id into a filesystem-safe, unique-per-test directory name."""
    cleaned = _UNSAFE.sub("_", node_id).strip("_")
    return cleaned[:_MAX_LEN] or "test"


class ArtifactManager:
    """Builds artifacts/<run_id>/<test>/ paths. Node ids are unique, so parallel workers
    never overwrite each other's files."""

    def __init__(self, root: Path, run_id: str) -> None:
        self._root = root
        self._run_id = run_id

    def test_dir(self, node_id: str) -> Path:
        path = self._root / self._run_id / safe_name(node_id)
        path.mkdir(parents=True, exist_ok=True)
        return path
