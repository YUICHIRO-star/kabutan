"""
Centralized configuration and runtime context helpers.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Literal, Optional

from dotenv import load_dotenv

LogLevel = Literal["INFO", "WARN", "ERROR", "DEBUG"]


@dataclass(frozen=True)
class RuntimeConfig:
    """User-configurable runtime options."""

    dry_run: bool
    run_id: str
    log_level: LogLevel

    @classmethod
    def from_env(cls, *, run_id: Optional[str] = None, log_level: Optional[str] = None, dry_run: Optional[bool] = None) -> "RuntimeConfig":
        load_dotenv()
        return cls(
            dry_run=bool(int(os.getenv("DRY_RUN", "0"))) if dry_run is None else dry_run,
            run_id=run_id or os.getenv("RUN_ID") or uuid.uuid4().hex,
            log_level=cast_log_level(log_level or os.getenv("LOG_LEVEL", "INFO")),
        )


def cast_log_level(value: str) -> LogLevel:
    upper = value.upper()
    if upper not in {"INFO", "WARN", "ERROR", "DEBUG"}:
        return "INFO"
    return upper  # type: ignore[return-value]
