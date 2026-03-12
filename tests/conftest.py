"""Test fixtures for filesystem plugin tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from business_assistant_filesystem.config import FilesystemSettings
from business_assistant_filesystem.service import FilesystemService


@pytest.fixture
def sample_tree(tmp_path: Path) -> Path:
    """Create a sample directory tree for testing."""
    # Create subdirectories
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "sub").mkdir()

    # Create files
    (tmp_path / "readme.md").write_text("# Hello", encoding="utf-8")
    (tmp_path / "docs" / "guide.txt").write_text("Guide content", encoding="utf-8")
    (tmp_path / "docs" / "notes.csv").write_text("a,b,c\n1,2,3", encoding="utf-8")
    (tmp_path / "src" / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "src" / "sub" / "util.py").write_text("x = 1", encoding="utf-8")
    (tmp_path / "data.bin").write_bytes(b"\x00\x01\x02")

    return tmp_path


@pytest.fixture
def settings(sample_tree: Path) -> FilesystemSettings:
    """Create FilesystemSettings pointing to the sample tree."""
    return FilesystemSettings(allowed_paths=(str(sample_tree),))


@pytest.fixture
def service(settings: FilesystemSettings) -> FilesystemService:
    """Create a FilesystemService from the test settings."""
    return FilesystemService(settings)
