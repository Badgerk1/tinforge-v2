from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .point import Point3D
from .triangle import Triangle


@dataclass(slots=True)
class TINModel:
    name: str = "Unnamed TIN"
    source: str = ""
    coordinate_system: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    points: list[Point3D] = field(default_factory=list)
    triangles: list[Triangle] = field(default_factory=list)
    breaklines: list[list[int]] = field(default_factory=list)
    boundary: list[tuple[float, float]] = field(default_factory=list)
    exclusion_zones: list[list[tuple[float, float]]] = field(default_factory=list)

    def add_point(self, point: Point3D) -> Point3D:
        point.validate()
        if point.point_id is None:
            next_id = max((existing.point_id or 0 for existing in self.points), default=0) + 1
            point.point_id = next_id
        if any(existing.point_id == point.point_id for existing in self.points):
            raise ValueError(f"duplicate point id: {point.point_id}")
        self.points.append(point)
        return point

    def add_triangle(self, triangle: Triangle) -> Triangle:
        triangle.validate_edges(self.point_lookup)
        if triangle.triangle_id is None:
            triangle.triangle_id = max((existing.triangle_id or 0 for existing in self.triangles), default=0) + 1
        if any(existing.triangle_id == triangle.triangle_id for existing in self.triangles):
            raise ValueError(f"duplicate triangle id: {triangle.triangle_id}")
        self.triangles.append(triangle)
        return triangle

    @property
    def point_lookup(self) -> dict[int, Point3D]:
        return {point.point_id: point for point in self.points if point.point_id is not None}

    @property
    def point_count(self) -> int:
        return len(self.points)

    @property
    def triangle_count(self) -> int:
        return len(self.triangles)

    def bounds(self) -> dict[str, float]:
        if not self.points:
            raise ValueError("TIN has no points")
        xs = [point.x for point in self.points]
        ys = [point.y for point in self.points]
        zs = [point.z for point in self.points]
        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
            "min_z": min(zs),
            "max_z": max(zs),
        }

    def total_2d_area(self) -> float:
        return sum(triangle.area_2d(self.point_lookup) for triangle in self.triangles)

    def statistics(self) -> dict[str, Any]:
        bounds = self.bounds() if self.points else {}
        return {
            "name": self.name,
            "point_count": self.point_count,
            "triangle_count": self.triangle_count,
            "breakline_count": len(self.breaklines),
            "boundary_vertex_count": len(self.boundary),
            "total_2d_area": self.total_2d_area(),
            "bounds": bounds,
            "coordinate_system": self.coordinate_system,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "coordinate_system": self.coordinate_system,
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
            "points": [point.to_dict() for point in self.points],
            "triangles": [
                {"point_ids": list(triangle.point_ids), "triangle_id": triangle.triangle_id}
                for triangle in self.triangles
            ],
            "breaklines": [list(line) for line in self.breaklines],
            "boundary": [list(vertex) for vertex in self.boundary],
            "exclusion_zones": [[list(vertex) for vertex in zone] for zone in self.exclusion_zones],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TINModel":
        model = cls(
            name=payload.get("name", "Unnamed TIN"),
            source=payload.get("source", ""),
            coordinate_system=payload.get("coordinate_system", ""),
            created_at=datetime.fromisoformat(payload["created_at"]) if payload.get("created_at") else datetime.now(timezone.utc),
            metadata=dict(payload.get("metadata", {})),
        )
        for point_payload in payload.get("points", []):
            model.add_point(Point3D.from_dict(point_payload))
        for triangle_payload in payload.get("triangles", []):
            model.add_triangle(
                Triangle(
                    point_ids=tuple(triangle_payload["point_ids"]),
                    triangle_id=triangle_payload.get("triangle_id"),
                )
            )
        model.breaklines = [list(line) for line in payload.get("breaklines", [])]
        model.boundary = [tuple(vertex) for vertex in payload.get("boundary", [])]
        model.exclusion_zones = [
            [tuple(vertex) for vertex in zone] for zone in payload.get("exclusion_zones", [])
        ]
        return model
