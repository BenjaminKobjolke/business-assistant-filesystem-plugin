"""Plugin registration — defines PydanticAI tools for filesystem operations."""

from __future__ import annotations

import logging

from business_assistant.agent.deps import Deps
from business_assistant.plugins.registry import PluginInfo, PluginRegistry
from pydantic_ai import RunContext, Tool

from .config import load_filesystem_settings
from .constants import (
    PLUGIN_CATEGORY,
    PLUGIN_DATA_FILESYSTEM_SERVICE,
    PLUGIN_DESCRIPTION,
    PLUGIN_NAME,
    SYSTEM_PROMPT_FILESYSTEM,
)
from .service import FilesystemService

logger = logging.getLogger(__name__)


def _get_service(ctx: RunContext[Deps]) -> FilesystemService:
    """Retrieve the FilesystemService from plugin_data."""
    return ctx.deps.plugin_data[PLUGIN_DATA_FILESYSTEM_SERVICE]


def _fs_search_files(
    ctx: RunContext[Deps], query: str, path: str | None = None
) -> str:
    """Recursive glob search for files within allowed paths.

    Use query for the glob pattern (e.g., "*.py", "report*").
    Optionally provide a path to limit the search scope to a specific directory.
    """
    logger.info("fs_search_files: query=%r path=%r", query, path)
    return _get_service(ctx).search_files(query, path)


def _fs_list_directory(ctx: RunContext[Deps], path: str) -> str:
    """List directory contents (files and subdirectories) at a given path."""
    logger.info("fs_list_directory: path=%r", path)
    return _get_service(ctx).list_directory(path)


def _fs_read_file(ctx: RunContext[Deps], path: str) -> str:
    """Read the text content of a file. Limited to 1 MB."""
    logger.info("fs_read_file: path=%r", path)
    return _get_service(ctx).read_file(path)


def _fs_write_file(ctx: RunContext[Deps], path: str, content: str) -> str:
    """Write or overwrite a text file. Only allowed for text file extensions."""
    logger.info("fs_write_file: path=%r", path)
    return _get_service(ctx).write_file(path, content)


def _fs_write_binary(ctx: RunContext[Deps], path: str, data: bytes) -> str:
    """Write binary data to a file. No extension restrictions."""
    logger.info("fs_write_binary: path=%r size=%d", path, len(data))
    return _get_service(ctx).write_binary(path, data)


def _fs_get_file(ctx: RunContext[Deps], path: str) -> str:
    """Upload a file to FTP and return a download URL for the user."""
    logger.info("fs_get_file: path=%r", path)
    ftp_service = ctx.deps.plugin_data.get("ftp_upload")
    return _get_service(ctx).get_file(path, ftp_service)


def _fs_create_directory(ctx: RunContext[Deps], path: str) -> str:
    """Create a directory (and parent directories). Returns status "created" or "exists"."""
    logger.info("fs_create_directory: path=%r", path)
    return _get_service(ctx).create_directory(path)


def _fs_file_operation(
    ctx: RunContext[Deps],
    action: str,
    source: str,
    destination: str = "",
) -> str:
    """File operations. action: copy, move, delete.

    destination required for copy/move.
    """
    svc = _get_service(ctx)
    if action == "copy":
        logger.info(
            "fs_file_operation copy: source=%r dest=%r",
            source, destination,
        )
        return svc.copy_file(source, destination)
    if action == "move":
        logger.info(
            "fs_file_operation move: source=%r dest=%r",
            source, destination,
        )
        return svc.move_file(source, destination)
    if action == "delete":
        logger.info("fs_file_operation delete: source=%r", source)
        return svc.delete_file(source)
    return f"Unknown action: {action!r}. Use copy, move, or delete."


def register(registry: PluginRegistry) -> None:
    """Register the filesystem plugin with the plugin registry.

    Reads FILESYSTEM_ALLOWED_PATHS from environment. Skips registration
    if not configured.
    """
    from business_assistant.config.log_setup import add_plugin_logging

    add_plugin_logging("filesystem", "business_assistant_filesystem")

    settings = load_filesystem_settings()
    if settings is None:
        logger.info("Filesystem plugin: FILESYSTEM_ALLOWED_PATHS not configured, skipping")
        return

    service = FilesystemService(settings)

    tools = [
        Tool(_fs_search_files, name="fs_search_files"),
        Tool(_fs_list_directory, name="fs_list_directory"),
        Tool(_fs_read_file, name="fs_read_file"),
        Tool(_fs_write_file, name="fs_write_file"),
        Tool(_fs_write_binary, name="fs_write_binary"),
        Tool(_fs_get_file, name="fs_get_file"),
        Tool(_fs_create_directory, name="fs_create_directory"),
        Tool(_fs_file_operation, name="fs_file_operation"),
    ]

    info = PluginInfo(
        name=PLUGIN_NAME,
        description=PLUGIN_DESCRIPTION,
        system_prompt_extra=SYSTEM_PROMPT_FILESYSTEM,
        category=PLUGIN_CATEGORY,
    )

    registry.register(info, tools)
    registry.plugin_data[PLUGIN_DATA_FILESYSTEM_SERVICE] = service

    logger.info("Filesystem plugin registered with %d tools", len(tools))
