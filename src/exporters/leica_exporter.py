from __future__ import annotations

import json
import struct

from src.core.tin_model import TINModel
from .base_exporter import BaseExporter


class LeicaDBXExporter(BaseExporter):
    extension = ".dbx"
    MAGIC = b"DBX\x00"
    VERSION = 1
    HEADER_STRUCT = struct.Struct("<4sHIII")
    POINT_STRUCT = struct.Struct("<I3dH")
    TRIANGLE_STRUCT = struct.Struct("<3I")

    def export_bytes(self, model: TINModel) -> bytes:
        self.validate_model(model)
        metadata_blob = json.dumps(
            {
                "name": model.name,
                "source": model.source,
                "coordinate_system": model.coordinate_system,
                **model.metadata,
            },
            sort_keys=True,
        ).encode("utf-8")
        chunks = [
            self.HEADER_STRUCT.pack(self.MAGIC, self.VERSION, model.point_count, model.triangle_count, len(metadata_blob)),
            metadata_blob,
        ]
        for point in sorted(model.points, key=lambda item: item.point_id or 0):
            description = point.description.encode("utf-8")
            chunks.append(self.POINT_STRUCT.pack(point.point_id or 0, point.x, point.y, point.z, len(description)))
            chunks.append(description)
        for triangle in sorted(model.triangles, key=lambda item: item.triangle_id or 0):
            chunks.append(self.TRIANGLE_STRUCT.pack(*triangle.point_ids))
        return b"".join(chunks)
