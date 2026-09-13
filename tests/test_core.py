import src.core.triangulation as triangulation_module
from src.core import DelaunayTriangulator, Point3D, TINModel, Triangle


SAMPLE_POINTS = [
    Point3D(0.0, 0.0, 100.0, point_id=1),
    Point3D(10.0, 0.0, 101.0, point_id=2),
    Point3D(0.0, 10.0, 102.0, point_id=3),
    Point3D(10.0, 10.0, 103.0, point_id=4),
]


def test_point_round_trip_and_validation():
    point = Point3D(1.0, 2.0, 3.0, point_id=10, description="BM", code="BM", attributes={"confidence": 0.95})
    assert Point3D.from_dict(point.to_dict()) == point


def test_triangle_area_normal_and_interpolation():
    lookup = {point.point_id: point for point in SAMPLE_POINTS}
    triangle = Triangle((1, 2, 3), triangle_id=1)
    assert triangle.area_2d(lookup) == 50.0
    assert round(triangle.area_3d(lookup), 6) > 50.0
    normal = triangle.normal_vector(lookup)
    assert len(normal) == 3
    assert round(sum(component * component for component in normal), 6) == 1.0
    assert triangle.barycentric_interpolate_z(2.5, 2.5, lookup) == 100.75


def test_tin_model_statistics_and_triangulation():
    result = DelaunayTriangulator().triangulate(SAMPLE_POINTS, name="Survey Surface")
    model = result.model
    assert model.point_count == 4
    assert model.triangle_count >= 2
    assert model.statistics()["name"] == "Survey Surface"
    assert model.bounds()["max_z"] == 103.0


def test_tin_model_serialization_round_trip():
    model = TINModel(name="Round Trip")
    for point in SAMPLE_POINTS[:3]:
        model.add_point(point)
    model.add_triangle(Triangle((1, 2, 3), triangle_id=7))
    restored = TINModel.from_dict(model.to_dict())
    assert restored.point_count == 3
    assert restored.triangle_count == 1


def test_triangulation_assigns_ids_for_points_without_ids():
    points = [
        Point3D(0.0, 0.0, 100.0),
        Point3D(10.0, 0.0, 101.0),
        Point3D(0.0, 10.0, 102.0),
    ]
    result = DelaunayTriangulator().triangulate(points)
    assert sorted(point.point_id for point in result.model.points) == [1, 2, 3]


def test_tin_model_rejects_duplicate_triangle_ids():
    model = TINModel(name="Triangle IDs")
    for point in SAMPLE_POINTS[:3]:
        model.add_point(point)
    model.add_triangle(Triangle((1, 2, 3), triangle_id=1))
    try:
        model.add_triangle(Triangle((1, 3, 2), triangle_id=1))
    except ValueError as exc:
        assert "duplicate triangle id" in str(exc)
    else:
        raise AssertionError("expected duplicate triangle id rejection")


def test_tin_model_auto_triangle_ids_follow_max_existing_id():
    model = TINModel(name="Triangle IDs")
    for point in SAMPLE_POINTS:
        model.add_point(point)
    model.add_triangle(Triangle((1, 2, 3), triangle_id=2))
    model.add_triangle(Triangle((2, 4, 3)))
    assert [triangle.triangle_id for triangle in model.triangles] == [2, 3]


def test_triangulation_falls_back_for_collinear_points():
    points = [
        Point3D(0.0, 0.0, 0.0, point_id=1),
        Point3D(1.0, 1.0, 1.0, point_id=2),
        Point3D(2.0, 2.0, 2.0, point_id=3),
    ]
    result = DelaunayTriangulator().triangulate(points)
    assert result.model.point_count == 3


def test_triangulation_reports_scipy_fallback(monkeypatch):
    points = [
        Point3D(0.0, 0.0, 0.0, point_id=1),
        Point3D(10.0, 0.0, 1.0, point_id=2),
        Point3D(0.0, 10.0, 2.0, point_id=3),
    ]

    def broken_delaunay(_coords):
        raise RuntimeError("forced failure")

    monkeypatch.setattr(triangulation_module, "ScipyDelaunay", broken_delaunay)
    result = DelaunayTriangulator().triangulate(points)
    assert result.model.point_count == 3
    assert result.warnings
    assert result.warnings[0] == "SciPy triangulation failed; used built-in fallback triangulation."


def test_triangulation_without_scipy_still_succeeds(monkeypatch):
    points = [
        Point3D(0.0, 0.0, 0.0, point_id=1),
        Point3D(10.0, 0.0, 1.0, point_id=2),
        Point3D(0.0, 10.0, 2.0, point_id=3),
    ]
    monkeypatch.setattr(triangulation_module, "ScipyDelaunay", None)
    result = DelaunayTriangulator().triangulate(points)
    assert result.model.point_count == 3
    assert result.warnings == []


def test_triangulation_emits_breakline_warning():
    result = DelaunayTriangulator().triangulate(
        SAMPLE_POINTS,
        breaklines=[[1, 2, 4]],
    )
    assert any("Breaklines are stored as metadata" in warning for warning in result.warnings)
