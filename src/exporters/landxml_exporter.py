from __future__ import annotations

from xml.etree import ElementTree as ET

from src.core.tin_model import TINModel
from .base_exporter import BaseExporter


class LandXMLExporter(BaseExporter):
    extension = ".xml"

    def export_bytes(self, model: TINModel) -> bytes:
        self.validate_model(model)
        root = ET.Element("LandXML", {"version": "1.2"})
        project = ET.SubElement(root, "Project", {"name": model.name})
        if model.coordinate_system:
            ET.SubElement(project, "CoordinateSystem").text = model.coordinate_system
        surfaces = ET.SubElement(root, "Surfaces")
        surface = ET.SubElement(surfaces, "Surface", {"name": model.name})
        definition = ET.SubElement(surface, "Definition", {"surfType": "TIN"})
        pnts = ET.SubElement(definition, "Pnts")
        for point in sorted(model.points, key=lambda item: item.point_id or 0):
            element = ET.SubElement(pnts, "P", {"id": str(point.point_id or 0)})
            element.text = f"{point.y:.6f} {point.x:.6f} {point.z:.6f}"
        faces = ET.SubElement(definition, "Faces")
        for triangle in sorted(model.triangles, key=lambda item: item.triangle_id or 0):
            face = ET.SubElement(faces, "F")
            face.text = " ".join(str(point_id) for point_id in triangle.point_ids)
        if hasattr(ET, "indent"):
            ET.indent(root)
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)
