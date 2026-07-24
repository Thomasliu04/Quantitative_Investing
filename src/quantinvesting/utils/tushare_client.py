from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

from quantinvesting.utils.config import project_root


@lru_cache(maxsize=1)
def get_tushare_token() -> str:
    load_dotenv(project_root() / ".env")
    token = os.getenv("TUSHARE_TOKEN", "").strip()
    if not token or token == "your_token_here":
        raise RuntimeError(
            "TUSHARE_TOKEN missing. Copy .env.example to .env and set your token."
        )
    return token
