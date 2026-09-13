from __future__ import annotations

from pathlib import Path

from src.core.tin_model import TINModel
from src.core.triangulation import DelaunayTriangulator
from src.exporters import ASCIIExporter, DXFExporter, LandXMLExporter, LeicaDBXExporter, TopconTP3Exporter
from src.parsers import CSVParser, PDFParser, TP3Parser


class TinForgeApp:
    def __init__(self) -> None:
        self.csv_parser = CSVParser()
        self.pdf_parser = PDFParser()
        self.tp3_parser = TP3Parser()
        self.triangulator = DelaunayTriangulator()
        self.exporters = {
            "tp3": TopconTP3Exporter(),
            "dbx": LeicaDBXExporter(),
            "landxml": LandXMLExporter(),
            "dxf": DXFExporter(),
            "ascii": ASCIIExporter(),
        }

    def import_points(self, path: str | Path):
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix == ".csv":
            return self.csv_parser.parse_file(path)
        if suffix == ".tp3":
            return self.tp3_parser.parse_file(path).points
        if suffix in {".pdf", ".txt"}:
            return self.pdf_parser.parse(path).points
        raise ValueError(f"unsupported input format: {path.suffix}")

    def generate_tin(self, path: str | Path, *, name: str = "Generated TIN") -> TINModel:
        points = self.import_points(path)
        return self.triangulator.triangulate(points, name=name).model

    def export(self, model: TINModel, output_dir: str | Path) -> dict[str, Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        written: dict[str, Path] = {}
        for name, exporter in self.exporters.items():
            output_path = output_dir / f"{model.name.replace(' ', '_').lower()}{exporter.extension}"
            exporter.export_file(model, output_path)
            written[name] = output_path
        return written
