from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Iterable

from src.core.point import Point3D


class CSVParser:
    FIELD_ALIASES = {
        "point_id": {"point_id", "id", "point", "pid"},
        "x": {"x", "e", "east", "easting"},
        "y": {"y", "n", "north", "northing"},
        "z": {"z", "elev", "elevation", "rl"},
        "description": {"description", "desc", "name"},
        "code": {"code", "feature_code", "layer"},
    }

    def parse_file(self, path: str | Path, delimiter: str | None = None) -> list[Point3D]:
        return self.parse_text(Path(path).read_text(encoding="utf-8"), delimiter=delimiter)

    def parse_text(self, text: str, delimiter: str | None = None) -> list[Point3D]:
        sample = text.strip()
        if not sample:
            return []
        chosen_delimiter = delimiter or self._detect_delimiter(sample)
        reader = csv.reader(StringIO(sample), delimiter=chosen_delimiter)
        rows = [row for row in reader if row and any(cell.strip() for cell in row)]
        if not rows:
            return []
        header_map = self._normalize_header(rows[0]) if self._looks_like_header(rows[0]) else None
        data_rows = rows[1:] if header_map else rows
        points = []
        for index, row in enumerate(data_rows, start=1):
            point = self._row_to_point(row, header_map, index)
            point.validate()
            points.append(point)
        return points

    def _row_to_point(self, row: list[str], header_map: dict[str, int] | None, row_number: int) -> Point3D:
        if header_map:
            get = lambda key, default="": row[header_map[key]].strip() if key in header_map and header_map[key] < len(row) else default
            point_id = int(get("point_id", row_number)) if get("point_id", "") else row_number
            return Point3D(
                point_id=point_id,
                x=float(get("x")),
                y=float(get("y")),
                z=float(get("z")),
                description=get("description"),
                code=get("code"),
            )
        if len(row) < 3:
            raise ValueError("point rows must contain at least X, Y, Z")
        return Point3D(
            point_id=row_number,
            x=float(row[0]),
            y=float(row[1]),
            z=float(row[2]),
            description=row[3].strip() if len(row) > 3 else "",
            code=row[4].strip() if len(row) > 4 else "",
        )

    def _looks_like_header(self, row: Iterable[str]) -> bool:
        lowered = {cell.strip().lower() for cell in row}
        return any(lowered & aliases for aliases in self.FIELD_ALIASES.values())

    def _normalize_header(self, row: list[str]) -> dict[str, int]:
        mapping: dict[str, int] = {}
        for index, cell in enumerate(row):
            lowered = cell.strip().lower()
            for canonical, aliases in self.FIELD_ALIASES.items():
                if lowered in aliases:
                    mapping[canonical] = index
                    break
        required = {"x", "y", "z"}
        if not required.issubset(mapping):
            raise ValueError("header must provide X, Y and Z columns")
        return mapping

    @staticmethod
    def _detect_delimiter(text: str) -> str:
        counts = {delimiter: text.count(delimiter) for delimiter in (",", "\t", ";", " ")}
        return max(counts, key=counts.get)
