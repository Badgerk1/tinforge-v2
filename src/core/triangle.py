from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from .point import Point3D


@dataclass(slots=True)
class Triangle:
    point_ids: tuple[int, int, int]
    triangle_id: int | None = None

    def __post_init__(self) -> None:
        if len(set(self.point_ids)) != 3:
            raise ValueError("triangle requires three unique point ids")

    def resolve_points(self, points: dict[int, Point3D] | Iterable[Point3D]) -> tuple[Point3D, Point3D, Point3D]:
        if isinstance(points, dict):
            lookup = points
        else:
            lookup = {point.point_id: point for point in points if point.point_id is not None}
        try:
            return tuple(lookup[point_id] for point_id in self.point_ids)  # type: ignore[return-value]
        except KeyError as exc:
            raise ValueError(f"missing point for triangle: {exc.args[0]}") from exc

    def area_2d(self, points: dict[int, Point3D] | Iterable[Point3D]) -> float:
        a, b, c = self.resolve_points(points)
        return abs(((b.x - a.x) * (c.y - a.y)) - ((c.x - a.x) * (b.y - a.y))) / 2.0

    def area_3d(self, points: dict[int, Point3D] | Iterable[Point3D]) -> float:
        a, b, c = self.resolve_points(points)
        ab = (b.x - a.x, b.y - a.y, b.z - a.z)
        ac = (c.x - a.x, c.y - a.y, c.z - a.z)
        cross = (
            ab[1] * ac[2] - ab[2] * ac[1],
            ab[2] * ac[0] - ab[0] * ac[2],
            ab[0] * ac[1] - ab[1] * ac[0],
        )
        return math.sqrt(sum(value * value for value in cross)) / 2.0

    def normal_vector(self, points: dict[int, Point3D] | Iterable[Point3D]) -> tuple[float, float, float]:
        a, b, c = self.resolve_points(points)
        ux, uy, uz = b.x - a.x, b.y - a.y, b.z - a.z
        vx, vy, vz = c.x - a.x, c.y - a.y, c.z - a.z
        nx, ny, nz = (
            uy * vz - uz * vy,
            uz * vx - ux * vz,
            ux * vy - uy * vx,
        )
        magnitude = math.sqrt(nx * nx + ny * ny + nz * nz)
        if magnitude == 0:
            raise ValueError("degenerate triangle has no normal")
        return (nx / magnitude, ny / magnitude, nz / magnitude)

    def barycentric_interpolate_z(self, x: float, y: float, points: dict[int, Point3D] | Iterable[Point3D]) -> float:
        a, b, c = self.resolve_points(points)
        denominator = ((b.y - c.y) * (a.x - c.x)) + ((c.x - b.x) * (a.y - c.y))
        if denominator == 0:
            raise ValueError("degenerate triangle cannot interpolate")
        w1 = (((b.y - c.y) * (x - c.x)) + ((c.x - b.x) * (y - c.y))) / denominator
        w2 = (((c.y - a.y) * (x - c.x)) + ((a.x - c.x) * (y - c.y))) / denominator
        w3 = 1 - w1 - w2
        return (w1 * a.z) + (w2 * b.z) + (w3 * c.z)

    def validate_edges(self, points: dict[int, Point3D] | Iterable[Point3D]) -> None:
        if self.area_2d(points) == 0:
            raise ValueError("triangle is degenerate in 2D")
