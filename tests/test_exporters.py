from xml.etree import ElementTree as ET

from src.core import Point3D, TINModel, Triangle
from src.exporters import ASCIIExporter, DXFExporter, LandXMLExporter, LeicaDBXExporter, TopconTP3Exporter
from src.parsers import TP3Parser


def build_model() -> TINModel:
    model = TINModel(name="Export Surface", coordinate_system="EPSG:2193")
    model.add_point(Point3D(0.0, 0.0, 1.0, point_id=1, description="A", code="A"))
    model.add_point(Point3D(10.0, 0.0, 2.0, point_id=2, description="B", code="B"))
    model.add_point(Point3D(0.0, 10.0, 3.0, point_id=3, description="C", code="C"))
    model.add_triangle(Triangle((1, 2, 3), triangle_id=1))
    return model


def test_topcon_export_round_trip():
    model = build_model()
    payload = TopconTP3Exporter().export_bytes(model)
    parsed = TP3Parser().parse_bytes(payload)
    assert parsed.point_count == model.point_count
    assert parsed.triangle_count == model.triangle_count
    assert parsed.coordinate_system == "EPSG:2193"


def test_leica_export_has_expected_magic():
    payload = LeicaDBXExporter().export_bytes(build_model())
    assert payload[:4] == b"DBX\x00"


def test_landxml_and_dxf_and_ascii_exports_are_populated():
    model = build_model()
    landxml = LandXMLExporter().export_bytes(model)
    root = ET.fromstring(landxml)
    assert root.tag == "LandXML"
    dxf = DXFExporter().export_bytes(model).decode("utf-8")
    assert "3DFACE" in dxf
    ascii_payload = ASCIIExporter().export_bytes(model).decode("utf-8")
    assert "point_id,x,y,z,description,code" in ascii_payload
