from src.core import Point3D, TINModel, Triangle
from src.validation import FormatValidator, TINValidator


def build_model() -> TINModel:
    model = TINModel(name="Validation Surface")
    model.add_point(Point3D(0.0, 0.0, 1.0, point_id=1))
    model.add_point(Point3D(10.0, 0.0, 2.0, point_id=2))
    model.add_point(Point3D(0.0, 10.0, 3.0, point_id=3))
    model.add_triangle(Triangle((1, 2, 3), triangle_id=1))
    return model


def test_tin_validator_accepts_valid_models():
    report = TINValidator().validate(build_model())
    assert report.is_valid is True
    assert report.errors == []


def test_format_validator_reports_differences():
    left = build_model()
    right = build_model()
    right.points[0].z = 10.0
    comparison = FormatValidator().compare_models(left, right)
    assert comparison.matches is False
    assert any("point 1 z differs" in item for item in comparison.differences)


def test_format_validator_reports_extra_point_ids():
    left = build_model()
    right = build_model()
    right.points[0].point_id = 99
    comparison = FormatValidator().compare_models(left, right)
    assert comparison.matches is False
    assert any("missing point in right model: 1" in item for item in comparison.differences)
