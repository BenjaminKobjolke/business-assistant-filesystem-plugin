"""Tests for plugin registration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from business_assistant_filesystem.constants import PLUGIN_DATA_FILESYSTEM_SERVICE, PLUGIN_NAME
from business_assistant_filesystem.service import FilesystemService


class TestRegister:
    def test_skips_when_unconfigured(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            from business_assistant_filesystem.plugin import register

            registry = MagicMock()
            registry.plugin_data = {}
            register(registry)
            registry.register.assert_not_called()

    def test_registers_when_configured(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        with patch.dict(
            "os.environ",
            {"FILESYSTEM_ALLOWED_PATHS": str(tmp_path)},
        ):
            from business_assistant_filesystem.plugin import register

            registry = MagicMock()
            registry.plugin_data = {}
            register(registry)

            registry.register.assert_called_once()
            call_args = registry.register.call_args
            info = call_args[0][0]
            tools = call_args[0][1]

            assert info.name == PLUGIN_NAME
            assert len(tools) == 8

            tool_names = {t.name for t in tools}
            assert tool_names == {
                "fs_search_files",
                "fs_list_directory",
                "fs_read_file",
                "fs_write_file",
                "fs_write_binary",
                "fs_get_file",
                "fs_create_directory",
                "fs_copy_file",
            }

    def test_stores_service_in_plugin_data(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        with patch.dict(
            "os.environ",
            {"FILESYSTEM_ALLOWED_PATHS": str(tmp_path)},
        ):
            from business_assistant_filesystem.plugin import register

            registry = MagicMock()
            registry.plugin_data = {}
            register(registry)

            assert PLUGIN_DATA_FILESYSTEM_SERVICE in registry.plugin_data
            assert isinstance(
                registry.plugin_data[PLUGIN_DATA_FILESYSTEM_SERVICE],
                FilesystemService,
            )
