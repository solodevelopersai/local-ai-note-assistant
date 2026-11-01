from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".mdx", ".rst", ".csv", ".json", ".yaml", ".yml"}


@dataclass
class NoteDocument:
    path: str
    filename: str
    extension: str
    text: str


class FileScanner:
    """Scan a directory tree for text-based note files that can be indexed by the AI assistant."""

    def __init__(self, root_dir: str, max_file_size: int = 2_000_000) -> None:
        self.root_dir = os.path.abspath(root_dir)
        self.max_file_size = max_file_size

    def _is_supported_file(self, file_name: str) -> bool:
        return Path(file_name).suffix.lower() in SUPPORTED_EXTENSIONS

    def _read_text_file(self, file_path: str) -> str | None:
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                return handle.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="utf-8-sig") as handle:
                    return handle.read()
            except (OSError, UnicodeDecodeError):
                return None
        except OSError:
            return None

    def scan_directory(self) -> list[NoteDocument]:
        if not os.path.isdir(self.root_dir):
            return []

        documents: list[NoteDocument] = []

        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            for file_name in sorted(files):
                if not self._is_supported_file(file_name):
                    continue

                file_path = os.path.join(root, file_name)
                if not os.path.isfile(file_path):
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                except OSError:
                    continue

                if file_size > self.max_file_size:
                    continue

                text = self._read_text_file(file_path)
                if text is None or not text.strip():
                    continue

                documents.append(
                    NoteDocument(
                        path=file_path,
                        filename=file_name,
                        extension=Path(file_name).suffix.lower(),
                        text=text,
                    )
                )

        return documents
