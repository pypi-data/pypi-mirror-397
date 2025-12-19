#!/usr/bin/env python3
#exonware/xwsystem/src/exonware/xwsystem/io/serialization/formats/text/jsonlines.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.411
Generation Date: 02-Nov-2025

JSON Lines (JSONL/NDJSON) Serialization - Newline-Delimited JSON

JSON Lines format (also called NDJSON - Newline Delimited JSON):
- One JSON object per line
- Perfect for streaming data
- Log file friendly
- Easy to append

Priority 1 (Security): Safe JSON parsing per line
Priority 2 (Usability): Streaming-friendly format
Priority 3 (Maintainability): Simple line-based processing
Priority 4 (Performance): Memory-efficient streaming
Priority 5 (Extensibility): Compatible with standard JSON
"""

from typing import Any, Optional, Union
from pathlib import Path
import json

from .json import JsonSerializer
from ....errors import SerializationError
from ....common.atomic import AtomicFileWriter


class JsonLinesSerializer(JsonSerializer):
    """
    JSON Lines (JSONL/NDJSON) serializer for streaming data.
    
    I: ISerialization (interface)
    A: ASerialization (abstract base)
    Concrete: JsonLinesSerializer
    """
    
    def __init__(self):
        """Initialize JSON Lines serializer."""
        super().__init__()
    
    @property
    def codec_id(self) -> str:
        """Codec identifier."""
        return "jsonl"
    
    @property
    def media_types(self) -> list[str]:
        """Supported MIME types."""
        return ["application/x-ndjson", "application/jsonl"]
    
    @property
    def file_extensions(self) -> list[str]:
        """Supported file extensions."""
        return [".jsonl", ".ndjson", ".jsonlines"]
    
    @property
    def aliases(self) -> list[str]:
        """Alternative names."""
        return ["jsonl", "JSONL", "ndjson", "NDJSON", "jsonlines"]
    
    @property
    def codec_types(self) -> list[str]:
        """JSON Lines is a data exchange format."""
        return ["data", "serialization"]

    # -------------------------------------------------------------------------
    # RECORD / STREAMING CAPABILITIES
    # -------------------------------------------------------------------------

    @property
    def supports_record_streaming(self) -> bool:
        """
        JSONL is explicitly designed for record-level streaming.

        This enables stream_read_record / stream_update_record to operate in a
        true streaming fashion (line-by-line) without loading the entire file.
        """
        return True

    @property
    def supports_record_paging(self) -> bool:
        """
        JSONL supports efficient record-level paging.

        Paging is implemented as a lightweight line counter that only parses
        the requested slice of records.
        """
        return True

    # -------------------------------------------------------------------------
    # CORE ENCODE / DECODE
    # -------------------------------------------------------------------------

    def encode(self, data: Any, *, options: Optional[dict[str, Any]] = None) -> str:
        """
        Encode data to JSON Lines string.
        
        Args:
            data: List of objects to encode (each becomes one line)
            options: Encoding options
            
        Returns:
            JSON Lines string (one JSON object per line)
        """
        if not isinstance(data, list):
            # Single object - wrap in list
            data = [data]

        opts = options or {}
        ensure_ascii = opts.get("ensure_ascii", False)

        lines: list[str] = []
        for item in data:
            lines.append(json.dumps(item, ensure_ascii=ensure_ascii))

        return "\n".join(lines)

    def decode(self, data: Union[str, bytes], *, options: Optional[dict[str, Any]] = None) -> list[Any]:
        """
        Decode JSON Lines string to list of Python objects.
        
        Args:
            data: JSON Lines string or bytes
            options: Decoding options
            
        Returns:
            List of decoded Python objects
        """
        if isinstance(data, bytes):
            data = data.decode("utf-8")

        # Split by newlines and parse each line
        lines = data.strip().split("\n")
        results: list[Any] = []

        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                results.append(json.loads(line))

        return results

    # -------------------------------------------------------------------------
    # RECORD-LEVEL OPERATIONS (True streaming, line-by-line)
    # -------------------------------------------------------------------------

    def stream_read_record(
        self,
        file_path: Union[str, Path],
        match: callable,
        projection: Optional[list[Any]] = None,
        **options: Any,
    ) -> Any:
        """
        Stream-style read of a single logical record from a JSONL file.

        Reads the file line-by-line, parsing each JSON object and returning the
        first record that satisfies match(record). Optional projection is
        applied using the base helper to avoid duplicating logic.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Line-by-line scan – no full-file load
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if match(record):
                    return self._apply_projection(record, projection)

        raise KeyError("No matching record found")

    def stream_update_record(
        self,
        file_path: Union[str, Path],
        match: callable,
        updater: callable,
        *,
        atomic: bool = True,
        **options: Any,
    ) -> int:
        """
        Stream-style update of logical records in a JSONL file.

        Implementation uses a temp file + AtomicFileWriter pattern to ensure
        atomicity when atomic=True. Records are processed line-by-line and only
        the matching records are materialized and updated.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        updated = 0
        backup = options.get("backup", True)
        ensure_ascii = options.get("ensure_ascii", False)

        try:
            if atomic:
                # Atomic path: use AtomicFileWriter for temp+replace semantics
                with AtomicFileWriter(path, backup=backup) as writer:
                    with path.open("r", encoding="utf-8") as src:
                        for line in src:
                            raw = line.rstrip("\n")
                            if not raw.strip():
                                # Preserve structural empty lines
                                writer.write(b"\n")
                                continue

                            record = json.loads(raw)
                            if match(record):
                                record = updater(record)
                                updated += 1

                            out_line = json.dumps(record, ensure_ascii=ensure_ascii) + "\n"
                            writer.write(out_line.encode("utf-8"))
            else:
                # Non-atomic fallback: read + rewrite line-by-line
                new_lines: list[str] = []
                with path.open("r", encoding="utf-8") as src:
                    for line in src:
                        raw = line.rstrip("\n")
                        if not raw.strip():
                            new_lines.append("\n")
                            continue

                        record = json.loads(raw)
                        if match(record):
                            record = updater(record)
                            updated += 1

                        new_lines.append(json.dumps(record, ensure_ascii=ensure_ascii) + "\n")

                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("".join(new_lines), encoding="utf-8")

            return updated
        except Exception as e:
            raise SerializationError(
                f"Failed to stream-update JSONL records in {path}: {e}",
                format_name=self.format_name,
                original_error=e,
            ) from e

    def get_record_page(
        self,
        file_path: Union[str, Path],
        page_number: int,
        page_size: int,
        **options: Any,
    ) -> list[Any]:
        """
        Retrieve a logical page of records from a JSONL file.

        Pages are computed by counting logical records (non-empty lines). Only
        the requested slice is parsed and returned, keeping memory usage
        proportional to page_size rather than file size.
        """
        if page_number < 1 or page_size <= 0:
            raise ValueError("Invalid page_number or page_size")

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size

        results: list[Any] = []
        current_index = 0

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if current_index >= end_index:
                    break

                if current_index >= start_index:
                    results.append(json.loads(line))

                current_index += 1

        return results

    def get_record_by_id(
        self,
        file_path: Union[str, Path],
        id_value: Any,
        *,
        id_field: str = "id",
        **options: Any,
    ) -> Any:
        """
        Retrieve a logical record by identifier from a JSONL file.

        Performs a streaming linear scan over records, returning the first
        record where record[id_field] == id_value.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                record = json.loads(line)
                if isinstance(record, dict) and record.get(id_field) == id_value:
                    return record

        raise KeyError(f"Record with {id_field}={id_value!r} not found")

