from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

from src.core.point import Point3D

try:
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pdfplumber = None


POINT_PATTERN = re.compile(
    r"^\s*(?P<id>\d+)\s+"
    r"(?P<x>-?\d+(?:\.\d+)?)\s+"
    r"(?P<y>-?\d+(?:\.\d+)?)\s+"
    r"(?P<z>-?\d+(?:\.\d+)?)"
    r"(?:\s+(?P<description>.*?))?\s*$"
)


@dataclass(slots=True)
class PDFParseResult:
    points: list[Point3D]
    metadata: dict[str, Any] = field(default_factory=dict)
    duplicates_removed: int = 0
    pages_processed: int = 0
    errors: list[str] = field(default_factory=list)

    def extraction_report(self) -> dict[str, Any]:
        return {
            "point_count": len(self.points),
            "duplicates_removed": self.duplicates_removed,
            "pages_processed": self.pages_processed,
            "errors": list(self.errors),
            "metadata": dict(self.metadata),
        }


class PDFParser:
    def parse(self, path: str | Path) -> PDFParseResult:
        path = Path(path)
        if path.suffix.lower() == ".txt":
            return self.parse_text(path.read_text(encoding="utf-8"), source_name=path.name)
        if pdfplumber is None:
            raise RuntimeError("pdfplumber is required to parse PDF files")
        pages: list[str] = []
        metadata: dict[str, Any] = {"source": path.name}
        with pdfplumber.open(path) as pdf:
            metadata.update({k: v for k, v in (pdf.metadata or {}).items() if v is not None})
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        result = self.parse_text("\n".join(pages), source_name=path.name)
        result.metadata.update(metadata)
        result.pages_processed = len(pages)
        return result

    def parse_text(self, text: str, *, source_name: str = "inline") -> PDFParseResult:
        seen_ids: set[int] = set()
        seen_records: dict[int, tuple[float, float, float, str]] = {}
        next_generated_id = 0
        points: list[Point3D] = []
        duplicates_removed = 0
        errors: list[str] = []
        for raw_line in text.splitlines():
            match = POINT_PATTERN.match(raw_line)
            if not match:
                continue
            point_id = int(match.group("id"))
            description = (match.group("description") or "").strip()
            code = description.split()[0] if description else ""
            x = float(match.group("x"))
            y = float(match.group("y"))
            z = float(match.group("z"))
            record = (x, y, z, description)
            if point_id in seen_ids:
                if seen_records[point_id] == record:
                    duplicates_removed += 1
                    continue
                next_generated_id = max(next_generated_id, max(seen_ids)) + 1
                replacement_id = next_generated_id
                errors.append(
                    f"Conflicting duplicate point id {point_id} found; preserved later observation as point {replacement_id}."
                )
                point_id = replacement_id
            seen_ids.add(point_id)
            if match and int(match.group("id")) not in seen_records:
                seen_records[int(match.group("id"))] = record
            points.append(
                Point3D(
                    point_id=point_id,
                    x=x,
                    y=y,
                    z=z,
                    description=description,
                    code=code,
                    attributes={"source": source_name},
                )
            )
        metadata = {"source": source_name, "parser": "regex-table-extractor"}
        return PDFParseResult(
            points=points,
            metadata=metadata,
            duplicates_removed=duplicates_removed,
            pages_processed=max(text.count("\f") + 1, 1 if text else 0),
            errors=errors,
        )
