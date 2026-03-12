# Business Assistant Filesystem Plugin - Development Guide

## Project Overview

Local filesystem plugin for Business Assistant v2. Source code in `src/business_assistant_filesystem/`.

## Commands

- `uv sync --all-extras` — Install dependencies
- `uv run pytest tests/ -v` — Run tests
- `uv run ruff check src/ tests/` — Lint
- `uv run mypy src/` — Type check

## Architecture

- `config.py` — FilesystemSettings (frozen dataclass)
- `constants.py` — Plugin-specific string constants
- `service.py` — FilesystemService with path validation + file operations
- `plugin.py` — Plugin registration + PydanticAI tool definitions
- `__init__.py` — Exposes `register()` as entry point

## Plugin Protocol

The plugin exposes `register(registry: PluginRegistry)` which:
1. Loads FILESYSTEM_ALLOWED_PATHS from env vars
2. Skips registration if not configured
3. Creates FilesystemService and registers 5 PydanticAI tools

## Restarting the Bot

After making code changes, always restart the bot by creating the restart flag:

```bash
touch "D:/GIT/BenjaminKobjolke/business-assistant-v2/restart.flag"
```

The bot picks it up within 5 seconds and restarts with fresh plugins.

## Rules

- Use objects for related values (DTOs/Settings)
- Centralize string constants in `constants.py`
- Tests are mandatory — use pytest
- Use `spec=` with MagicMock
- Type hints on all public APIs
- All file operations must validate paths against allowed directories
