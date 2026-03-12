# Business Assistant Filesystem Plugin

Local filesystem plugin for [Business Assistant v2](https://github.com/BenjaminKobjolke/business-assistant-v2). Provides tools for searching, reading, writing, and downloading files from configured directories.

## Setup

1. Run `install.bat` to create the virtual environment and install dependencies
2. Copy `.env.example` to `.env` in your business-assistant-v2 directory
3. Set `FILESYSTEM_ALLOWED_PATHS` to comma-separated absolute paths
4. Add `business_assistant_filesystem` to the `PLUGINS` list in your business-assistant-v2 `.env`

## Configuration

| Variable | Description |
|----------|-------------|
| `FILESYSTEM_ALLOWED_PATHS` | Comma-separated absolute paths the plugin may access |

## Tools

| Tool | Description |
|------|-------------|
| `fs_search_files` | Recursive glob search within allowed paths |
| `fs_list_directory` | List directory contents |
| `fs_read_file` | Read text file content (max 1 MB) |
| `fs_write_file` | Write/overwrite text files (text extensions only) |
| `fs_get_file` | Upload file to FTP, return download URL |

## Security

- All paths are validated against `FILESYSTEM_ALLOWED_PATHS`
- Path traversal (`../`) is blocked via `Path.resolve()` + `is_relative_to()`
- Write operations restricted to text file extensions
- Read operations limited to 1 MB

## Development

```bash
uv sync --all-extras        # Install dependencies
uv run pytest tests/ -v     # Run tests
uv run ruff check src/ tests/  # Lint
uv run mypy src/            # Type check
```
