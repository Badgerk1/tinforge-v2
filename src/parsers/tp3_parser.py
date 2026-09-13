from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import struct
from typing import Any

from src.core.point import Point3D
from src.core.tin_model import TINModel
from src.core.triangle import Triangle


class TP3Parser:
    MAGIC = b"TP3\x00"
    HEADER_STRUCT = struct.Struct("<4sHIII")
    SUPPORTED_VERSION = 1
    POINT_STRUCT = struct.Struct("<IdddHH")
    TRIANGLE_STRUCT = struct.Struct("<IIII")

    def parse_file(self, path: str | Path) -> TINModel:
        return self.parse_bytes(Path(path).read_bytes())

    def parse_bytes(self, payload: bytes) -> TINModel:
        if len(payload) < self.HEADER_STRUCT.size:
            raise ValueError("payload is too small to contain a TP3 header")
        magic, version, point_count, triangle_count, metadata_length = self.HEADER_STRUCT.unpack_from(payload, 0)
        if magic != self.MAGIC:
            raise ValueError("not a supported TP3 file")
        if version != self.SUPPORTED_VERSION:
            raise ValueError(f"unsupported TP3 version: {version}")
        offset = self.HEADER_STRUCT.size
        if len(payload) < offset + metadata_length:
            raise ValueError("payload is truncated before TP3 metadata")
        try:
            metadata = json.loads(payload[offset : offset + metadata_length].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("payload contains invalid TP3 metadata") from exc
        offset += metadata_length
        minimum_length = offset + (point_count * self.POINT_STRUCT.size) + (triangle_count * self.TRIANGLE_STRUCT.size)
        if len(payload) < minimum_length:
            raise ValueError("payload is truncated before TP3 records")
        model = TINModel(
            name=metadata.get("name", "Imported TP3"),
            source=metadata.get("source", ""),
            coordinate_system=metadata.get("coordinate_system", ""),
            created_at=datetime.fromisoformat(metadata["created_at"]) if metadata.get("created_at") else datetime.now(timezone.utc),
            metadata=metadata,
        )
        for _ in range(point_count):
            point_id, x, y, z, description_length, code_length = self.POINT_STRUCT.unpack_from(payload, offset)
            offset += self.POINT_STRUCT.size
            if len(payload) < offset + description_length + code_length:
                raise ValueError("payload is truncated inside TP3 point data")
            description = payload[offset : offset + description_length].decode("utf-8")
            offset += description_length
            code = payload[offset : offset + code_length].decode("utf-8")
            offset += code_length
            model.add_point(Point3D(point_id=point_id, x=x, y=y, z=z, description=description, code=code))
        for _ in range(triangle_count):
            triangle_id, p1, p2, p3 = self.TRIANGLE_STRUCT.unpack_from(payload, offset)
            offset += self.TRIANGLE_STRUCT.size
            model.add_triangle(Triangle(point_ids=(p1, p2, p3), triangle_id=triangle_id))
        if offset != len(payload):
            raise ValueError("payload contains trailing data after TP3 records")
        return model

    def analyze_structure(self, payload: bytes) -> dict[str, Any]:
        if len(payload) < self.HEADER_STRUCT.size:
            raise ValueError("payload is too small to contain a TP3 header")
        magic, version, point_count, triangle_count, metadata_length = self.HEADER_STRUCT.unpack_from(payload, 0)
        return {
            "magic": magic.decode("latin1"),
            "version": version,
            "point_count": point_count,
            "triangle_count": triangle_count,
            "metadata_length": metadata_length,
            "file_size": len(payload),
        }
