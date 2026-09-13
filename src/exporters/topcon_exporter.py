from __future__ import annotations

import json
import struct

from src.core.tin_model import TINModel
from .base_exporter import BaseExporter


class TopconTP3Exporter(BaseExporter):
    extension = ".tp3"
    MAGIC = b"TP3\x00"
    VERSION = 1
    HEADER_STRUCT = struct.Struct("<4sHIII")
    POINT_STRUCT = struct.Struct("<IdddHH")
    TRIANGLE_STRUCT = struct.Struct("<IIII")

    def export_bytes(self, model: TINModel) -> bytes:
        self.validate_model(model)
        metadata = {
            "name": model.name,
            "source": model.source,
            "coordinate_system": model.coordinate_system,
            **model.metadata,
        }
        metadata_blob = json.dumps(metadata, sort_keys=True).encode("utf-8")
        chunks = [
            self.HEADER_STRUCT.pack(
                self.MAGIC,
                self.VERSION,
                model.point_count,
                model.triangle_count,
                len(metadata_blob),
            ),
            metadata_blob,
        ]
        for point in sorted(model.points, key=lambda item: item.point_id or 0):
            description = point.description.encode("utf-8")
            code = point.code.encode("utf-8")
            chunks.append(self.POINT_STRUCT.pack(point.point_id or 0, point.x, point.y, point.z, len(description), len(code)))
            chunks.append(description)
            chunks.append(code)
        for triangle in sorted(model.triangles, key=lambda item: item.triangle_id or 0):
            chunks.append(
                self.TRIANGLE_STRUCT.pack(
                    triangle.triangle_id or 0,
                    triangle.point_ids[0],
                    triangle.point_ids[1],
                    triangle.point_ids[2],
                )
            )
        return b"".join(chunks)
