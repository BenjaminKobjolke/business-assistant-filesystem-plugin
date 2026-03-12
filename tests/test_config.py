"""Tests for config.py — settings loading from environment."""

from __future__ import annotations

from unittest.mock import patch

from business_assistant_filesystem.config import load_filesystem_settings


class TestLoadFilesystemSettings:
    def test_returns_none_when_not_set(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            assert load_filesystem_settings() is None

    def test_returns_none_when_empty(self) -> None:
        with patch.dict("os.environ", {"FILESYSTEM_ALLOWED_PATHS": ""}):
            assert load_filesystem_settings() is None

    def test_returns_none_when_whitespace_only(self) -> None:
        with patch.dict("os.environ", {"FILESYSTEM_ALLOWED_PATHS": "  , , "}):
            assert load_filesystem_settings() is None

    def test_parses_single_path(self) -> None:
        with patch.dict("os.environ", {"FILESYSTEM_ALLOWED_PATHS": "D:\\Documents"}):
            settings = load_filesystem_settings()
            assert settings is not None
            assert settings.allowed_paths == ("D:\\Documents",)

    def test_parses_multiple_paths(self) -> None:
        with patch.dict(
            "os.environ",
            {"FILESYSTEM_ALLOWED_PATHS": "D:\\Documents,E:\\Projects"},
        ):
            settings = load_filesystem_settings()
            assert settings is not None
            assert settings.allowed_paths == ("D:\\Documents", "E:\\Projects")

    def test_strips_whitespace(self) -> None:
        with patch.dict(
            "os.environ",
            {"FILESYSTEM_ALLOWED_PATHS": " D:\\Docs , E:\\Work "},
        ):
            settings = load_filesystem_settings()
            assert settings is not None
            assert settings.allowed_paths == ("D:\\Docs", "E:\\Work")

    def test_settings_is_frozen(self) -> None:
        with patch.dict("os.environ", {"FILESYSTEM_ALLOWED_PATHS": "D:\\Docs"}):
            settings = load_filesystem_settings()
            assert settings is not None
            import pytest
            with pytest.raises(AttributeError):
                settings.allowed_paths = ("X:\\Other",)  # type: ignore[misc]
