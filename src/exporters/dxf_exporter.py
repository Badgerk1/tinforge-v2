from __future__ import annotations

from src.core.tin_model import TINModel
from .base_exporter import BaseExporter


class DXFExporter(BaseExporter):
    extension = ".dxf"

    def export_bytes(self, model: TINModel) -> bytes:
        self.validate_model(model)
        lines = ["0", "SECTION", "2", "ENTITIES"]
        lookup = model.point_lookup
        for triangle in model.triangles:
            points = [lookup[point_id] for point_id in triangle.point_ids]
            lines.extend(["0", "3DFACE", "8", "TIN"])
            for point_index, point in enumerate(points + [points[2]], start=0):
                base = 10 + point_index
                lines.extend([
                    str(base), f"{point.x}",
                    str(base + 10), f"{point.y}",
                    str(base + 20), f"{point.z}",
                ])
        lines.extend(["0", "ENDSEC", "0", "EOF"])
        return ("\n".join(lines) + "\n").encode("utf-8")
