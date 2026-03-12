"""Filesystem service — path validation and file operations."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from .config import FilesystemSettings
from .constants import (
    ERR_DESTINATION_EXISTS,
    ERR_FILE_TOO_LARGE,
    ERR_FTP_NOT_AVAILABLE,
    ERR_NOT_A_DIRECTORY,
    ERR_NOT_A_FILE,
    ERR_PATH_NOT_ALLOWED,
    ERR_SOURCE_NOT_FOUND,
    ERR_WRITE_EXTENSION_NOT_ALLOWED,
    MAX_READ_SIZE_BYTES,
    TEXT_EXTENSIONS,
)

logger = logging.getLogger(__name__)


class FilesystemService:
    """File operations restricted to configured allowed paths."""

    def __init__(self, settings: FilesystemSettings) -> None:
        self._allowed_paths = tuple(Path(p).resolve() for p in settings.allowed_paths)

    def _validate_path(self, path_str: str) -> Path | str:
        """Validate and resolve a path. Returns resolved Path or error string."""
        resolved = Path(path_str).resolve()
        for allowed in self._allowed_paths:
            if resolved == allowed or resolved.is_relative_to(allowed):
                return resolved
        return ERR_PATH_NOT_ALLOWED.format(path=path_str)

    def search_files(self, query: str, path: str | None = None) -> str:
        """Recursive glob search within allowed paths."""
        results: list[str] = []

        if path is not None:
            validated = self._validate_path(path)
            if isinstance(validated, str):
                return validated
            if not validated.is_dir():
                return ERR_NOT_A_DIRECTORY.format(path=path)
            search_roots = [validated]
        else:
            search_roots = list(self._allowed_paths)

        for root in search_roots:
            if not root.is_dir():
                continue
            for match in root.rglob(query):
                results.append(str(match))

        return json.dumps({"query": query, "count": len(results), "files": results})

    def list_directory(self, path: str) -> str:
        """List directory contents."""
        validated = self._validate_path(path)
        if isinstance(validated, str):
            return validated
        if not validated.is_dir():
            return ERR_NOT_A_DIRECTORY.format(path=path)

        entries: list[dict[str, str]] = []
        for item in sorted(validated.iterdir()):
            entries.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "path": str(item),
            })

        return json.dumps({"path": str(validated), "count": len(entries), "entries": entries})

    def read_file(self, path: str) -> str:
        """Read text file content."""
        validated = self._validate_path(path)
        if isinstance(validated, str):
            return validated
        if not validated.is_file():
            return ERR_NOT_A_FILE.format(path=path)

        size = validated.stat().st_size
        if size > MAX_READ_SIZE_BYTES:
            return ERR_FILE_TOO_LARGE.format(size=size, max_size=MAX_READ_SIZE_BYTES)

        content = validated.read_text(encoding="utf-8")
        return json.dumps({"path": str(validated), "size": size, "content": content})

    def write_file(self, path: str, content: str) -> str:
        """Write or overwrite a text file."""
        validated = self._validate_path(path)
        if isinstance(validated, str):
            return validated

        ext = validated.suffix.lower()
        if ext not in TEXT_EXTENSIONS:
            return ERR_WRITE_EXTENSION_NOT_ALLOWED.format(ext=ext)

        validated.parent.mkdir(parents=True, exist_ok=True)
        validated.write_text(content, encoding="utf-8")
        size = len(content.encode("utf-8"))
        return json.dumps({"path": str(validated), "size": size, "status": "written"})

    def create_directory(self, path: str) -> str:
        """Create a directory (and parents). Returns JSON with path and status."""
        validated = self._validate_path(path)
        if isinstance(validated, str):
            return validated

        if validated.is_dir():
            return json.dumps({"path": str(validated), "status": "exists"})

        validated.mkdir(parents=True, exist_ok=True)
        return json.dumps({"path": str(validated), "status": "created"})

    def copy_file(self, source: str, destination: str) -> str:
        """Copy a file from source to destination.

        Both must be within allowed paths. Creates parent directories if needed.
        Returns JSON with source, destination, size, and status.
        """
        validated_src = self._validate_path(source)
        if isinstance(validated_src, str):
            return validated_src
        if not validated_src.is_file():
            return ERR_SOURCE_NOT_FOUND.format(path=source)

        validated_dst = self._validate_path(destination)
        if isinstance(validated_dst, str):
            return validated_dst
        if validated_dst.exists():
            return ERR_DESTINATION_EXISTS.format(path=destination)

        validated_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(validated_src), str(validated_dst))
        size = validated_dst.stat().st_size
        return json.dumps({
            "source": str(validated_src),
            "destination": str(validated_dst),
            "size": size,
            "status": "copied",
        })

    def get_file(self, path: str, ftp_service: object | None) -> str:
        """Upload a file to FTP and return the download URL."""
        if ftp_service is None:
            return ERR_FTP_NOT_AVAILABLE

        validated = self._validate_path(path)
        if isinstance(validated, str):
            return validated
        if not validated.is_file():
            return ERR_NOT_A_FILE.format(path=path)

        data = validated.read_bytes()
        url = ftp_service.upload(data, validated.name)  # type: ignore[union-attr]
        return json.dumps({"path": str(validated), "filename": validated.name, "url": url})
