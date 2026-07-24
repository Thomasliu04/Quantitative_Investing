from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    """Repo root: .../Quantinvesting (contains configs/, src/, data/)."""
    return Path(__file__).resolve().parents[3]


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path else project_root() / "configs" / "data.yaml"
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_path(rel: str | Path) -> Path:
    p = Path(rel)
    if p.is_absolute():
        return p
    return project_root() / p
