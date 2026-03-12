"""Tests for service.py — FilesystemService operations."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from business_assistant_filesystem.service import FilesystemService


class TestValidatePath:
    def test_allows_path_within_allowed_dir(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        result = service._validate_path(str(sample_tree / "readme.md"))
        assert isinstance(result, Path)

    def test_allows_allowed_root_itself(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        result = service._validate_path(str(sample_tree))
        assert isinstance(result, Path)

    def test_rejects_path_outside_allowed(self, service: FilesystemService, tmp_path: Path) -> None:
        outside = tmp_path.parent / "outside"
        result = service._validate_path(str(outside))
        assert isinstance(result, str)
        assert "Access denied" in result

    def test_rejects_traversal_attack(self, service: FilesystemService, sample_tree: Path) -> None:
        attack = str(sample_tree / "docs" / ".." / ".." / "etc" / "passwd")
        result = service._validate_path(attack)
        assert isinstance(result, str)
        assert "Access denied" in result


class TestSearchFiles:
    def test_search_all_py_files(self, service: FilesystemService) -> None:
        result = json.loads(service.search_files("*.py"))
        assert result["count"] == 2
        names = [Path(f).name for f in result["files"]]
        assert sorted(names) == ["main.py", "util.py"]

    def test_search_with_path_scope(self, service: FilesystemService, sample_tree: Path) -> None:
        result = json.loads(service.search_files("*.py", str(sample_tree / "src" / "sub")))
        assert result["count"] == 1
        assert Path(result["files"][0]).name == "util.py"

    def test_search_no_matches(self, service: FilesystemService) -> None:
        result = json.loads(service.search_files("*.xyz"))
        assert result["count"] == 0

    def test_search_invalid_path(self, service: FilesystemService, tmp_path: Path) -> None:
        outside = str(tmp_path.parent / "nope")
        result = service.search_files("*", outside)
        assert "Access denied" in result

    def test_search_path_not_a_directory(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        result = service.search_files("*", str(sample_tree / "readme.md"))
        assert "Not a directory" in result


class TestListDirectory:
    def test_list_root(self, service: FilesystemService, sample_tree: Path) -> None:
        result = json.loads(service.list_directory(str(sample_tree)))
        names = [e["name"] for e in result["entries"]]
        assert "readme.md" in names
        assert "docs" in names
        assert "src" in names

    def test_entries_have_type(self, service: FilesystemService, sample_tree: Path) -> None:
        result = json.loads(service.list_directory(str(sample_tree)))
        types = {e["name"]: e["type"] for e in result["entries"]}
        assert types["docs"] == "directory"
        assert types["readme.md"] == "file"

    def test_rejects_outside_path(self, service: FilesystemService, tmp_path: Path) -> None:
        result = service.list_directory(str(tmp_path.parent / "nope"))
        assert "Access denied" in result

    def test_rejects_file_as_directory(self, service: FilesystemService, sample_tree: Path) -> None:
        result = service.list_directory(str(sample_tree / "readme.md"))
        assert "Not a directory" in result


class TestReadFile:
    def test_read_text_file(self, service: FilesystemService, sample_tree: Path) -> None:
        result = json.loads(service.read_file(str(sample_tree / "readme.md")))
        assert result["content"] == "# Hello"

    def test_rejects_nonexistent(self, service: FilesystemService, sample_tree: Path) -> None:
        result = service.read_file(str(sample_tree / "nope.txt"))
        assert "Not a file" in result

    def test_rejects_outside_path(self, service: FilesystemService, tmp_path: Path) -> None:
        result = service.read_file(str(tmp_path.parent / "secret.txt"))
        assert "Access denied" in result

    def test_rejects_too_large(self, service: FilesystemService, sample_tree: Path) -> None:
        big = sample_tree / "big.txt"
        big.write_bytes(b"x" * 1_048_577)
        result = service.read_file(str(big))
        assert "too large" in result


class TestWriteFile:
    def test_write_new_file(self, service: FilesystemService, sample_tree: Path) -> None:
        target = str(sample_tree / "new.txt")
        result = json.loads(service.write_file(target, "hello world"))
        assert result["status"] == "written"
        assert Path(target).read_text(encoding="utf-8") == "hello world"

    def test_overwrite_existing(self, service: FilesystemService, sample_tree: Path) -> None:
        target = str(sample_tree / "readme.md")
        service.write_file(target, "updated")
        assert Path(target).read_text(encoding="utf-8") == "updated"

    def test_creates_parent_dirs(self, service: FilesystemService, sample_tree: Path) -> None:
        target = str(sample_tree / "new_dir" / "sub" / "file.json")
        result = json.loads(service.write_file(target, '{"key": "val"}'))
        assert result["status"] == "written"

    def test_rejects_binary_extension(self, service: FilesystemService, sample_tree: Path) -> None:
        result = service.write_file(str(sample_tree / "file.exe"), "data")
        assert "Write denied" in result

    def test_rejects_outside_path(self, service: FilesystemService, tmp_path: Path) -> None:
        result = service.write_file(str(tmp_path.parent / "evil.txt"), "data")
        assert "Access denied" in result


class TestWriteBinary:
    def test_write_binary_file(self, service: FilesystemService, sample_tree: Path) -> None:
        target = str(sample_tree / "output.bin")
        data = b"\x00\x01\x02\xff"
        result = json.loads(service.write_binary(target, data))
        assert result["status"] == "written"
        assert result["size"] == 4
        assert Path(target).read_bytes() == data

    def test_creates_parent_dirs(self, service: FilesystemService, sample_tree: Path) -> None:
        target = str(sample_tree / "new_dir" / "sub" / "file.pdf")
        result = json.loads(service.write_binary(target, b"pdfdata"))
        assert result["status"] == "written"
        assert Path(target).read_bytes() == b"pdfdata"

    def test_rejects_outside_path(self, service: FilesystemService, tmp_path: Path) -> None:
        result = service.write_binary(str(tmp_path.parent / "evil.bin"), b"data")
        assert "Access denied" in result


class TestCreateDirectory:
    def test_creates_new_directory(self, service: FilesystemService, sample_tree: Path) -> None:
        target = str(sample_tree / "new_dir")
        result = json.loads(service.create_directory(target))
        assert result["status"] == "created"
        assert Path(target).is_dir()

    def test_creates_nested_directories(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        target = str(sample_tree / "a" / "b" / "c")
        result = json.loads(service.create_directory(target))
        assert result["status"] == "created"
        assert Path(target).is_dir()

    def test_existing_directory_returns_exists(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        result = json.loads(service.create_directory(str(sample_tree / "docs")))
        assert result["status"] == "exists"

    def test_rejects_outside_path(self, service: FilesystemService, tmp_path: Path) -> None:
        result = service.create_directory(str(tmp_path.parent / "outside_dir"))
        assert "Access denied" in result


class TestCopyFile:
    def test_copies_file(self, service: FilesystemService, sample_tree: Path) -> None:
        src = str(sample_tree / "readme.md")
        dst = str(sample_tree / "readme_copy.md")
        result = json.loads(service.copy_file(src, dst))
        assert result["status"] == "copied"
        assert result["size"] > 0
        assert Path(dst).read_text(encoding="utf-8") == "# Hello"

    def test_creates_parent_dirs(self, service: FilesystemService, sample_tree: Path) -> None:
        src = str(sample_tree / "readme.md")
        dst = str(sample_tree / "nested" / "deep" / "copy.md")
        result = json.loads(service.copy_file(src, dst))
        assert result["status"] == "copied"
        assert Path(dst).is_file()

    def test_rejects_source_outside_allowed(
        self, service: FilesystemService, tmp_path: Path,
    ) -> None:
        result = service.copy_file(str(tmp_path.parent / "secret.txt"), str(tmp_path / "out.txt"))
        assert "Access denied" in result

    def test_rejects_destination_outside_allowed(
        self, service: FilesystemService, sample_tree: Path, tmp_path: Path,
    ) -> None:
        src = str(sample_tree / "readme.md")
        result = service.copy_file(src, str(tmp_path.parent / "evil.txt"))
        assert "Access denied" in result

    def test_rejects_nonexistent_source(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        src = str(sample_tree / "nonexistent.txt")
        dst = str(sample_tree / "copy.txt")
        result = service.copy_file(src, dst)
        assert "Source file not found" in result

    def test_rejects_existing_destination(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        src = str(sample_tree / "readme.md")
        dst = str(sample_tree / "docs" / "guide.txt")
        result = service.copy_file(src, dst)
        assert "Destination already exists" in result


class TestDeleteFile:
    def test_deletes_file(self, service: FilesystemService, sample_tree: Path) -> None:
        target = sample_tree / "readme.md"
        assert target.is_file()
        result = json.loads(service.delete_file(str(target)))
        assert result["status"] == "deleted"
        assert not target.exists()

    def test_rejects_directory(self, service: FilesystemService, sample_tree: Path) -> None:
        result = service.delete_file(str(sample_tree / "docs"))
        assert "Cannot delete directory" in result

    def test_rejects_nonexistent(self, service: FilesystemService, sample_tree: Path) -> None:
        result = service.delete_file(str(sample_tree / "nope.txt"))
        assert "Not a file" in result

    def test_rejects_outside_path(self, service: FilesystemService, tmp_path: Path) -> None:
        result = service.delete_file(str(tmp_path.parent / "secret.txt"))
        assert "Access denied" in result


class TestMoveFile:
    def test_moves_file(self, service: FilesystemService, sample_tree: Path) -> None:
        src = str(sample_tree / "readme.md")
        dst = str(sample_tree / "moved.md")
        result = json.loads(service.move_file(src, dst))
        assert result["status"] == "moved"
        assert result["size"] > 0
        assert Path(dst).read_text(encoding="utf-8") == "# Hello"
        assert not Path(src).exists()

    def test_creates_parent_dirs(self, service: FilesystemService, sample_tree: Path) -> None:
        src = str(sample_tree / "readme.md")
        dst = str(sample_tree / "nested" / "deep" / "moved.md")
        result = json.loads(service.move_file(src, dst))
        assert result["status"] == "moved"
        assert Path(dst).is_file()
        assert not Path(src).exists()

    def test_rejects_source_outside_allowed(
        self, service: FilesystemService, tmp_path: Path,
    ) -> None:
        result = service.move_file(
            str(tmp_path.parent / "secret.txt"), str(tmp_path / "out.txt"),
        )
        assert "Access denied" in result

    def test_rejects_destination_outside_allowed(
        self, service: FilesystemService, sample_tree: Path, tmp_path: Path,
    ) -> None:
        src = str(sample_tree / "readme.md")
        result = service.move_file(src, str(tmp_path.parent / "evil.txt"))
        assert "Access denied" in result

    def test_rejects_nonexistent_source(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        result = service.move_file(
            str(sample_tree / "nonexistent.txt"), str(sample_tree / "dst.txt"),
        )
        assert "Source file not found" in result

    def test_rejects_existing_destination(
        self, service: FilesystemService, sample_tree: Path,
    ) -> None:
        src = str(sample_tree / "readme.md")
        dst = str(sample_tree / "docs" / "guide.txt")
        result = service.move_file(src, dst)
        assert "Destination already exists" in result


class TestGetFile:
    def test_uploads_and_returns_url(self, service: FilesystemService, sample_tree: Path) -> None:
        ftp = MagicMock()
        ftp.upload.return_value = "https://example.com/abc_readme.md"
        result = json.loads(service.get_file(str(sample_tree / "readme.md"), ftp))
        assert result["url"] == "https://example.com/abc_readme.md"
        ftp.upload.assert_called_once()
        call_args = ftp.upload.call_args
        assert call_args[0][0] == b"# Hello"
        assert call_args[0][1] == "readme.md"

    def test_returns_error_without_ftp(self, service: FilesystemService, sample_tree: Path) -> None:
        result = service.get_file(str(sample_tree / "readme.md"), None)
        assert "not configured" in result

    def test_rejects_nonexistent_file(self, service: FilesystemService, sample_tree: Path) -> None:
        ftp = MagicMock()
        result = service.get_file(str(sample_tree / "nope.txt"), ftp)
        assert "Not a file" in result

    def test_rejects_outside_path(self, service: FilesystemService, tmp_path: Path) -> None:
        ftp = MagicMock()
        result = service.get_file(str(tmp_path.parent / "secret.bin"), ftp)
        assert "Access denied" in result
