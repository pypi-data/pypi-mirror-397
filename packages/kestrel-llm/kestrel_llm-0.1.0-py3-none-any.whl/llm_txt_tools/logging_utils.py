"""Shared logging helpers for LLM maintenance utilities."""

from __future__ import annotations

import logging
import os

DEFAULT_LOG_FORMAT = "%(message)s"
DEFAULT_LOG_LEVEL = logging.INFO
LOG_LEVEL_ENV = "LOG_LEVEL"


def _resolve_level(level: str | int | None) -> int:
    """Return a numeric log level, honoring an optional env override."""
    candidate: str | int | None = level
    if candidate is None:
        env_level = os.environ.get(LOG_LEVEL_ENV)
        if env_level:
            candidate = env_level

    if isinstance(candidate, int):
        return candidate

    if isinstance(candidate, str):
        resolved = logging.getLevelName(candidate.upper())
        if isinstance(resolved, int):
            return resolved

    return DEFAULT_LOG_LEVEL


def setup_logging(level: str | int | None = None, *, force: bool = True) -> None:
    """Configure root logging with a minimal, CLI-friendly format.

    - Defaults to INFO level, or respects LOG_LEVEL if set.
    - Uses force=True by default so repeated calls remain predictable.
    """
    resolved_level = _resolve_level(level)
    logging.basicConfig(level=resolved_level, format=DEFAULT_LOG_FORMAT, force=force)
