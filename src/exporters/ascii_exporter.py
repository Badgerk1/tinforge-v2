from __future__ import annotations

import csv
from io import StringIO

from src.core.tin_model import TINModel
from .base_exporter import BaseExporter


class ASCIIExporter(BaseExporter):
    extension = ".csv"

    def __init__(self, delimiter: str = ",", include_header: bool = True) -> None:
        self.delimiter = delimiter
        self.include_header = include_header

    def export_bytes(self, model: TINModel) -> bytes:
        self.validate_model(model)
        buffer = StringIO()
        writer = csv.writer(buffer, delimiter=self.delimiter)
        if self.include_header:
            writer.writerow(["point_id", "x", "y", "z", "description", "code"])
        for point in sorted(model.points, key=lambda item: item.point_id or 0):
            writer.writerow([point.point_id, point.x, point.y, point.z, point.description, point.code])
        return buffer.getvalue().encode("utf-8")
