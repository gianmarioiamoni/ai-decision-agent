import os
import pytest

from app.rag.context_loader import ContextLoader
from app.rag.file_manager import FileManager


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

class FakeFileManager(FileManager):
    #
    # Minimal FileManager override for testing.
    #
    def __init__(self, files):
        self._files = files

    def get_files(self):
        return self._files


# ---------------------------------------------------------
# FIX 5 TESTS
# ---------------------------------------------------------

def test_no_files_returns_empty_context(monkeypatch):
    #
    # No files at all -> RAG must be disabled
    #
    fm = FakeFileManager(files=[])

    monkeypatch.setattr(
        "app.rag.context_loader.get_file_manager",
        lambda: fm,
    )

    loader = ContextLoader()
    docs = loader.load()

    assert docs == []


def test_missing_file_is_skipped(tmp_path, monkeypatch):
    #
    # File in registry but missing on disk -> skipped
    #
    files = [
        {
            "name": "missing.txt",
            "path": tmp_path / "missing.txt",
        }
    ]

    fm = FakeFileManager(files=files)

    monkeypatch.setattr(
        "app.rag.context_loader.get_file_manager",
        lambda: fm,
    )

    loader = ContextLoader()
    docs = loader.load()

    assert docs == []


def test_empty_file_is_skipped(tmp_path, monkeypatch):
    #
    # Empty file -> skipped
    #
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    files = [
        {
            "name": "empty.txt",
            "path": str(empty_file),
        }
    ]

    fm = FakeFileManager(files=files)

    monkeypatch.setattr(
        "app.rag.context_loader.get_file_manager",
        lambda: fm,
    )

    loader = ContextLoader()
    docs = loader.load()

    assert docs == []


def test_valid_file_is_loaded(tmp_path, monkeypatch):
    # 1️⃣ Create real file
    file_path = tmp_path / "valid.txt"
    file_path.write_text("This is valid content", encoding="utf-8")

    # 2️⃣ Fake FileManager
    class FakeFileManager:
        def get_files(self):
            return [
                {
                    "name": "valid.txt",
                    "path": str(file_path),  # 🔑 MUST be real path
                }
            ]

    # 3️⃣ Patch get_file_manager used by ContextLoader
    monkeypatch.setattr(
        "app.rag.context_loader.get_file_manager",
        lambda: FakeFileManager()
    )

    loader = ContextLoader()
    docs = loader.load()

    assert len(docs) == 1
    assert "This is valid content" in docs[0]
