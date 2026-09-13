from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from src.core.tin_model import TINModel


class BaseExporter(ABC):
    extension = ""

    def validate_model(self, model: TINModel) -> None:
        if model.point_count == 0:
            raise ValueError("TIN model must contain at least one point")
        for triangle in model.triangles:
            triangle.validate_edges(model.point_lookup)

    @abstractmethod
    def export_bytes(self, model: TINModel) -> bytes:
        raise NotImplementedError

    def export_file(self, model: TINModel, path: str | Path) -> Path:
        self.validate_model(model)
        output_path = Path(path)
        output_path.write_bytes(self.export_bytes(model))
        return output_path
