from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Iterable

from .point import Point3D
from .triangle import Triangle
from .tin_model import TINModel

try:
    from scipy.spatial import Delaunay as ScipyDelaunay  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ScipyDelaunay = None


@dataclass(slots=True)
class TriangulationResult:
    model: TINModel
    quality_metrics: dict[str, float]
    statistics: dict[str, float]
    warnings: list[str] = field(default_factory=list)


class DelaunayTriangulator:
    def triangulate(
        self,
        points: Iterable[Point3D],
        *,
        name: str = "Generated TIN",
        breaklines: list[list[int]] | None = None,
        boundary: list[tuple[float, float]] | None = None,
    ) -> TriangulationResult:
        source_points = list(points)
        if len(source_points) < 3:
            raise ValueError("at least three points are required")

        model = TINModel(name=name)
        for point in source_points:
            model.add_point(
                Point3D(
                    x=point.x,
                    y=point.y,
                    z=point.z,
                    point_id=point.point_id,
                    description=point.description,
                    code=point.code,
                    attributes=dict(point.attributes),
                )
            )

        simplices, triangulation_warnings = self._compute_simplices(model.points)
        for simplex in simplices:
            triangle = Triangle(point_ids=tuple(simplex))
            if triangle.area_2d(model.point_lookup) > 0:
                model.add_triangle(triangle)

        if breaklines:
            model.breaklines = [list(line) for line in breaklines]
        if boundary:
            model.boundary = list(boundary)

        areas = [triangle.area_2d(model.point_lookup) for triangle in model.triangles]
        quality_metrics = {
            "triangle_count": float(model.triangle_count),
            "min_triangle_area": min(areas) if areas else 0.0,
            "max_triangle_area": max(areas) if areas else 0.0,
            "average_triangle_area": sum(areas) / len(areas) if areas else 0.0,
        }
        statistics = {
            "point_count": float(model.point_count),
            "triangle_count": float(model.triangle_count),
            "breakline_count": float(len(model.breaklines)),
        }
        warnings: list[str] = list(triangulation_warnings)
        if breaklines:
            warnings.append("Breaklines are stored as metadata and should be enforced by a constrained triangulator in a future release.")
        return TriangulationResult(model=model, quality_metrics=quality_metrics, statistics=statistics, warnings=warnings)

    def _compute_simplices(self, points: list[Point3D]) -> tuple[list[tuple[int, int, int]], list[str]]:
        for index, point in enumerate(points, start=1):
            if point.point_id is None:
                point.point_id = index
        if ScipyDelaunay is not None:
            try:
                coords = [(point.x, point.y) for point in points]
                delaunay = ScipyDelaunay(coords)
                ids = [point.point_id for point in points]
                return [tuple(ids[int(index)] for index in simplex) for simplex in delaunay.simplices], []
            except Exception as exc:
                _ = exc
                return self._bowyer_watson(points), ["SciPy triangulation failed; used built-in fallback triangulation."]
        return self._bowyer_watson(points), []

    def _bowyer_watson(self, points: list[Point3D]) -> list[tuple[int, int, int]]:
        indexed = [(point.point_id, point.x, point.y) for point in points if point.point_id is not None]
        xs = [x for _, x, _ in indexed]
        ys = [y for _, _, y in indexed]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        delta = max(max_x - min_x, max_y - min_y) or 1.0
        mid_x = (min_x + max_x) / 2.0
        mid_y = (min_y + max_y) / 2.0

        super_triangle = [
            (-1, mid_x - 20 * delta, mid_y - delta),
            (-2, mid_x, mid_y + 20 * delta),
            (-3, mid_x + 20 * delta, mid_y - delta),
        ]
        all_points = indexed + super_triangle
        triangles = [(-1, -2, -3)]

        for point_id, px, py in indexed:
            bad_triangles = []
            for triangle in triangles:
                if self._in_circumcircle((px, py), triangle, all_points):
                    bad_triangles.append(triangle)
            polygon: list[tuple[int, int]] = []
            for triangle in bad_triangles:
                for edge in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
                    if (edge[1], edge[0]) in polygon:
                        polygon.remove((edge[1], edge[0]))
                    elif edge in polygon:
                        polygon.remove(edge)
                    else:
                        polygon.append(edge)
            triangles = [triangle for triangle in triangles if triangle not in bad_triangles]
            for edge in polygon:
                triangles.append((edge[0], edge[1], point_id))

        result = []
        for triangle in triangles:
            if any(point_id < 0 for point_id in triangle):
                continue
            if self._triangle_area(triangle, all_points) > 0:
                result.append(triangle)
        unique = []
        seen = set()
        for triangle in result:
            key = tuple(sorted(triangle))
            if key not in seen:
                unique.append(triangle)
                seen.add(key)
        return unique

    @staticmethod
    def _triangle_area(triangle: tuple[int, int, int], points: list[tuple[int, float, float]]) -> float:
        lookup = {point_id: (x, y) for point_id, x, y in points}
        (ax, ay), (bx, by), (cx, cy) = (lookup[triangle[0]], lookup[triangle[1]], lookup[triangle[2]])
        return abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2.0

    @staticmethod
    def _in_circumcircle(point: tuple[float, float], triangle: tuple[int, int, int], points: list[tuple[int, float, float]]) -> bool:
        lookup = {point_id: (x, y) for point_id, x, y in points}
        ax, ay = lookup[triangle[0]]
        bx, by = lookup[triangle[1]]
        cx, cy = lookup[triangle[2]]
        px, py = point

        ax -= px
        ay -= py
        bx -= px
        by -= py
        cx -= px
        cy -= py

        det = (
            (ax * ax + ay * ay) * (bx * cy - cx * by)
            - (bx * bx + by * by) * (ax * cy - cx * ay)
            + (cx * cx + cy * cy) * (ax * by - bx * ay)
        )
        orientation = (lookup[triangle[1]][0] - lookup[triangle[0]][0]) * (lookup[triangle[2]][1] - lookup[triangle[0]][1]) - (
            lookup[triangle[2]][0] - lookup[triangle[0]][0]
        ) * (lookup[triangle[1]][1] - lookup[triangle[0]][1])
        return det > 0 if orientation > 0 else det < 0
