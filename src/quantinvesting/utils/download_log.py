from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DownloadLog:
    """Track completed download keys for resume support.

    Keys are strings like ``daily:20240102`` or ``fina_indicator_vip:20231231``.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._done: set[str] = set()
        self._meta: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._done = set(data.get("done", []))
        self._meta = data.get("meta", {})

    def save(self) -> None:
        payload = {"done": sorted(self._done), "meta": self._meta}
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def has(self, key: str) -> bool:
        return key in self._done

    def mark(self, key: str, *, flush: bool = True) -> None:
        self._done.add(key)
        if flush:
            self.save()

    def set_meta(self, **kwargs: Any) -> None:
        self._meta.update(kwargs)
        self.save()
