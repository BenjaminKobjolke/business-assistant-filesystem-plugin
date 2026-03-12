"""Plugin-specific string constants."""

# Environment variable names
ENV_FILESYSTEM_ALLOWED_PATHS = "FILESYSTEM_ALLOWED_PATHS"

# Plugin name and category
PLUGIN_NAME = "filesystem"
PLUGIN_CATEGORY = "filesystem"
PLUGIN_DESCRIPTION = "Local filesystem operations"

# Plugin data keys
PLUGIN_DATA_FILESYSTEM_SERVICE = "filesystem_service"

# Limits
MAX_READ_SIZE_BYTES = 1_048_576  # 1 MB

# Allowed text extensions for writing
TEXT_EXTENSIONS = frozenset({
    ".txt", ".md", ".csv", ".json", ".xml", ".yaml", ".yml",
    ".ini", ".cfg", ".conf", ".log", ".bat", ".sh", ".py",
    ".js", ".ts", ".html", ".css", ".sql", ".toml",
})

# Error messages
ERR_PATH_NOT_ALLOWED = "Access denied: path '{path}' is not within allowed directories."
ERR_PATH_NOT_FOUND = "Path not found: '{path}'"
ERR_NOT_A_FILE = "Not a file: '{path}'"
ERR_NOT_A_DIRECTORY = "Not a directory: '{path}'"
ERR_FILE_TOO_LARGE = "File too large: {size} bytes (max {max_size} bytes)"
ERR_WRITE_EXTENSION_NOT_ALLOWED = (
    "Write denied: extension '{ext}' is not in the allowed text extensions list."
)
ERR_NO_ALLOWED_PATHS = "No allowed paths configured."
ERR_FTP_NOT_AVAILABLE = "FTP upload service is not configured."
ERR_SOURCE_NOT_FOUND = "Source file not found: '{path}'"
ERR_DESTINATION_EXISTS = "Destination already exists: '{path}'"
ERR_DELETE_IS_DIRECTORY = (
    "Cannot delete directory with fs_delete_file: '{path}'. "
    "Only files can be deleted."
)

# System prompt extra
SYSTEM_PROMPT_FILESYSTEM = """You have access to local filesystem tools:
- fs_search_files: Recursive glob search for files. Use query for the pattern \
(e.g., "*.py", "report*"). Optionally provide a path to limit the search scope.
- fs_list_directory: List directory contents (files and subdirectories) at a given path.
- fs_read_file: Read the text content of a file. Limited to 1 MB.
- fs_write_file: Write or overwrite a text file. Only allowed for text file extensions \
(.txt, .md, .csv, .json, .xml, .yaml, .yml, .ini, .cfg, .conf, .log, .bat, .sh, .py, \
.js, .ts, .html, .css, .sql, .toml).
- fs_write_binary: Write binary data to a file at a given path. Unlike fs_write_file, \
this has no extension restrictions — use it for binary files (images, PDFs, etc.).
- fs_get_file: Upload a file to FTP and return a download URL for the user.
- fs_create_directory: Create a directory (and parent directories). \
Returns status "created" or "exists".
- fs_copy_file: Copy a file from source to destination. Both paths must be within \
allowed paths. Creates parent directories if needed. Preserves file metadata.
- fs_delete_file: Delete a file. Only files can be deleted, not directories.
- fs_move_file: Move or rename a file from source to destination. Both paths must be \
within allowed paths. Creates parent directories if needed.

All filesystem operations are restricted to configured allowed paths. \
Attempting to access files outside those paths will be denied.

When the user asks to find, search, read, edit, delete, move, rename, \
or download files on their local system, use these tools."""
