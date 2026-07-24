from __future__ import annotations

from typing import Any

from loguru import logger

from quantinvesting.utils.config import resolve_path


class QlibDumper:
    """Skeleton: convert clean panels into Qlib bin provider format.

    Implementation later can wrap ``qlib.run.get_data DumpDataAll`` or a custom dump.
    """

    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.clean_root = resolve_path(cfg["paths"]["clean"])
        self.qlib_root = resolve_path(cfg["paths"]["qlib"])

    def run(self, *, dry_run: bool = True) -> None:
        if dry_run:
            logger.info(
                "[dry-run] would dump clean data from {} -> qlib provider {}",
                self.clean_root,
                self.qlib_root,
            )
            return
        logger.warning("Qlib dump not implemented yet")
