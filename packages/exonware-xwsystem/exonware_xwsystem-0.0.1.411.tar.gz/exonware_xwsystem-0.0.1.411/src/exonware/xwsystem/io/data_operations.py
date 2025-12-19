#!/usr/bin/env python3
"""
#exonware/xwsystem/src/exonware/xwsystem/io/data_operations.py

Generic data-operations layer for large, file-backed datasets.

This module provides:
- A small indexing model for line-oriented files (e.g. NDJSON / JSONL)
- Streaming read / update helpers with atomic guarantees
- Paging helpers built on top of line offsets

The goal is to expose these capabilities in a format-agnostic way so that
higher-level libraries (xwdata, xwnode, xwentity, etc.) can build powerful
lazy, paged, and atomic access features without re-implementing I/O logic.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.411
Generation Date: 15-Dec-2025
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional
from abc import ABC, abstractmethod
import json
import os
import tempfile

from .serialization.auto_serializer import AutoSerializer
from ..config.logging_setup import get_logger


logger = get_logger(__name__)


JsonMatchFn = Callable[[Any], bool]
JsonUpdateFn = Callable[[Any], Any]


@dataclass
class JsonIndexMeta:
    """
    Minimal metadata for a JSONL/NDJSON index.

    This intentionally mirrors the capabilities used in the x5 examples
    without pulling in any of the example code directly.
    """

    path: str
    size: int
    mtime: float
    version: int = 1


@dataclass
class JsonIndex:
    """
    Simple index for line-oriented JSON files.

    - line_offsets: byte offset of each JSON line
    - id_index: optional mapping id_value -> line_number
    """

    meta: JsonIndexMeta
    line_offsets: list[int]
    id_index: Optional[dict[str, int]] = None


class ADataOperations(ABC):
    """
    Abstract, format-agnostic interface for large, file-backed data operations.

    Concrete implementations may target specific physical layouts
    (NDJSON/JSONL, multi-document YAML, binary record stores, etc.), but MUST
    conform to these semantics:

    - Streaming, record-by-record read with a match predicate.
    - Streaming, atomic update using a temp file + replace pattern.
    - Optional indexing for random access and paging.
    """

    @abstractmethod
    def stream_read(
        self,
        file_path: str | Path,
        match: JsonMatchFn,
        path: Optional[list[object]] = None,
        encoding: str = "utf-8",
    ) -> Any:
        """Return the first record (or sub-path) that matches the predicate."""
        raise NotImplementedError

    @abstractmethod
    def stream_update(
        self,
        file_path: str | Path,
        match: JsonMatchFn,
        updater: JsonUpdateFn,
        *,
        encoding: str = "utf-8",
        newline: str = "\n",
        atomic: bool = True,
    ) -> int:
        """
        Stream-copy the backing store, applying `updater` to matching records.

        MUST use atomic replace semantics when `atomic=True`.
        Returns number of updated records.
        """
        raise NotImplementedError

    @abstractmethod
    def build_index(
        self,
        file_path: str | Path,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
    ) -> JsonIndex:
        """Build an index structure suitable for random access and paging."""
        raise NotImplementedError

    @abstractmethod
    def indexed_get_by_line(
        self,
        file_path: str | Path,
        line_number: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """Random-access a specific logical record by its index position."""
        raise NotImplementedError

    @abstractmethod
    def indexed_get_by_id(
        self,
        file_path: str | Path,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """Random-access a record by logical identifier, with optional index."""
        raise NotImplementedError

    @abstractmethod
    def get_page(
        self,
        file_path: str | Path,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> list[Any]:
        """Return a page of logical records using an index for efficiency."""
        raise NotImplementedError


class NDJSONDataOperations(ADataOperations):
    """
    Generic data-operations helper for NDJSON / JSONL style files.

    This class is deliberately low-level and works directly with paths and
    native Python data. XWData and other libraries can wrap it to provide
    higher-level, type-agnostic facades.
    """

    def __init__(self, serializer: Optional[AutoSerializer] = None):
        # Reuse xwsystem's AutoSerializer so we do not re-implement parsing.
        self._serializer = serializer or AutoSerializer(default_format="JSON")

    # ------------------------------------------------------------------
    # Streaming read
    # ------------------------------------------------------------------

    def stream_read(
        self,
        file_path: str | Path,
        match: JsonMatchFn,
        path: Optional[list[object]] = None,
        encoding: str = "utf-8",
    ) -> Any:
        """
        Stream a huge NDJSON file and return the first record (or sub-path)
        matching `match`.

        This is intentionally simple and focused:
        - Reads one line at a time
        - Uses AutoSerializer(JSON) for parsing
        - Optional path extraction
        """
        target = Path(file_path)
        if not target.exists():
            raise FileNotFoundError(str(target))

        with target.open("r", encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = self._serializer.detect_and_deserialize(
                    line, file_path=target, format_hint="JSON"
                )
                if match(obj):
                    return self._extract_path(obj, path)

        raise KeyError("No matching record found")

    # ------------------------------------------------------------------
    # Streaming update with atomic replace
    # ------------------------------------------------------------------

    def stream_update(
        self,
        file_path: str | Path,
        match: JsonMatchFn,
        updater: JsonUpdateFn,
        *,
        encoding: str = "utf-8",
        newline: str = "\n",
        atomic: bool = True,
    ) -> int:
        """
        Stream-copy a huge NDJSON file, applying `updater` to records
        where `match(obj)` is True.

        Only matching records are fully materialized. All writes go to a
        temporary file, which is atomically replaced on success.

        Returns the number of updated records.
        """
        target = Path(file_path)
        if not target.exists():
            raise FileNotFoundError(str(target))

        updated = 0
        dir_path = target.parent

        # Write to a temp file in the same directory for atomic replace.
        fd, tmp_path_str = tempfile.mkstemp(
            prefix=f".{target.name}.tmp.", dir=str(dir_path)
        )
        tmp_path = Path(tmp_path_str)

        try:
            with os.fdopen(fd, "w", encoding=encoding, newline=newline) as out_f, target.open(
                "r", encoding=encoding
            ) as in_f:
                for line in in_f:
                    raw = line.rstrip("\n")
                    if not raw:
                        out_f.write(line)
                        continue

                    obj = self._serializer.detect_and_deserialize(
                        raw, file_path=target, format_hint="JSON"
                    )
                    if match(obj):
                        updated_obj = updater(obj)
                        updated_line = json.dumps(updated_obj, ensure_ascii=False)
                        out_f.write(updated_line + newline)
                        updated += 1
                    else:
                        out_f.write(line)

            if atomic:
                os.replace(tmp_path, target)
            else:
                tmp_path.replace(target)

            return updated
        finally:
            # Ensure temp file is removed on error
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    # Best-effort cleanup; do not mask original error.
                    logger.debug("Failed to cleanup temp file %s", tmp_path)

    # ------------------------------------------------------------------
    # Indexing and paging
    # ------------------------------------------------------------------

    def build_index(
        self,
        file_path: str | Path,
        *,
        encoding: str = "utf-8",
        id_field: str | None = None,
        max_id_index: int | None = None,
    ) -> JsonIndex:
        """
        One-time full scan to build an index:
          - line_offsets: byte offset of each JSON line
          - optional id_index: obj[id_field] -> line_number
        """
        target = Path(file_path)
        if not target.exists():
            raise FileNotFoundError(str(target))

        line_offsets: list[int] = []
        id_index: dict[str, int] | None = {} if id_field else None

        size = target.stat().st_size
        mtime = target.stat().st_mtime

        offset = 0
        with target.open("rb") as f:
            line_no = 0
            while True:
                line = f.readline()
                if not line:
                    break
                line_offsets.append(offset)

                if id_index is not None:
                    try:
                        text = line.decode(encoding).strip()
                        if text:
                            obj = self._serializer.detect_and_deserialize(
                                text, file_path=target, format_hint="JSON"
                            )
                            if isinstance(obj, dict) and id_field in obj:
                                id_val = str(obj[id_field])
                                if max_id_index is None or len(id_index) < max_id_index:
                                    id_index[id_val] = line_no
                    except Exception:
                        # Index should be best-effort and robust to bad lines.
                        logger.debug("Skipping line %s while building id index", line_no)

                offset += len(line)
                line_no += 1

        meta = JsonIndexMeta(path=str(target), size=size, mtime=mtime, version=1)
        return JsonIndex(meta=meta, line_offsets=line_offsets, id_index=id_index)

    def indexed_get_by_line(
        self,
        file_path: str | Path,
        line_number: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """
        Random-access a specific record by line_number (0-based) using index.
        """
        target = Path(file_path)
        if index is None:
            index = self.build_index(target, encoding=encoding)

        if line_number < 0 or line_number >= len(index.line_offsets):
            raise IndexError("line_number out of range")

        offset = index.line_offsets[line_number]
        with target.open("rb") as f:
            f.seek(offset)
            line = f.readline()
            text = line.decode(encoding).strip()
            if not text:
                raise ValueError("Empty line at indexed position")
            return self._serializer.detect_and_deserialize(
                text, file_path=target, format_hint="JSON"
            )

    def indexed_get_by_id(
        self,
        file_path: str | Path,
        id_value: Any,
        *,
        encoding: str = "utf-8",
        id_field: str = "id",
        index: Optional[JsonIndex] = None,
    ) -> Any:
        """
        Random-access a record by logical id using id_index if available.
        Falls back to linear scan if id_index missing or incomplete.
        """
        target = Path(file_path)
        if index is None:
            index = self.build_index(target, encoding=encoding, id_field=id_field)

        id_index = index.id_index
        if id_index is not None:
            key = str(id_value)
            if key in id_index:
                return self.indexed_get_by_line(
                    target, id_index[key], encoding=encoding, index=index
                )

        # Fallback: linear scan using stream_read semantics
        def _match(obj: Any) -> bool:
            return isinstance(obj, dict) and obj.get(id_field) == id_value

        return self.stream_read(target, _match, path=None, encoding=encoding)

    def get_page(
        self,
        file_path: str | Path,
        page_number: int,
        page_size: int,
        *,
        encoding: str = "utf-8",
        index: Optional[JsonIndex] = None,
    ) -> list[Any]:
        """
        Paging helper using index:
          - page_number: 1-based
          - page_size: number of records per page
        """
        target = Path(file_path)
        if index is None:
            index = self.build_index(target, encoding=encoding)

        if page_number < 1 or page_size <= 0:
            raise ValueError("Invalid page_number or page_size")

        start = (page_number - 1) * page_size
        end = start + page_size

        if start >= len(index.line_offsets):
            return []

        end = min(end, len(index.line_offsets))

        results: list[Any] = []
        with target.open("rb") as f:
            for line_no in range(start, end):
                offset = index.line_offsets[line_no]
                f.seek(offset)
                line = f.readline()
                text = line.decode(encoding).strip()
                if not text:
                    continue
                obj = self._serializer.detect_and_deserialize(
                    text, file_path=target, format_hint="JSON"
                )
                results.append(obj)

        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_path(self, obj: Any, path: Optional[list[object]]) -> Any:
        """Extract a nested path like ['user', 'email'] or ['tags', 0]."""
        if not path:
            return obj

        current = obj
        for part in path:
            if isinstance(current, dict) and isinstance(part, str):
                if part not in current:
                    raise KeyError(part)
                current = current[part]
            elif isinstance(current, list) and isinstance(part, int):
                current = current[part]
            else:
                raise KeyError(part)
        return current


__all__ = [
    "JsonIndexMeta",
    "JsonIndex",
    "ADataOperations",
    "NDJSONDataOperations",
]


