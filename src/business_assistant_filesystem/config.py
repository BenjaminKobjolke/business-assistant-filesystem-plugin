"""Filesystem settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .constants import ENV_FILESYSTEM_ALLOWED_PATHS


@dataclass(frozen=True)
class FilesystemSettings:
    """Filesystem plugin settings."""

    allowed_paths: tuple[str, ...]


def load_filesystem_settings() -> FilesystemSettings | None:
    """Load filesystem settings from environment variables.

    Returns None if FILESYSTEM_ALLOWED_PATHS is not configured.
    """
    raw = os.environ.get(ENV_FILESYSTEM_ALLOWED_PATHS, "")
    if not raw.strip():
        return None

    paths = tuple(p.strip() for p in raw.split(",") if p.strip())
    if not paths:
        return None

    return FilesystemSettings(allowed_paths=paths)
