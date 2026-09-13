from __future__ import annotations

from dataclasses import dataclass, field

from src.core.tin_model import TINModel


@dataclass(slots=True)
class FormatComparison:
    matches: bool
    differences: list[str] = field(default_factory=list)


class FormatValidator:
    def compare_models(self, left: TINModel, right: TINModel, tolerance: float = 1e-6) -> FormatComparison:
        differences: list[str] = []
        if left.point_count != right.point_count:
            differences.append(f"point count differs: {left.point_count} != {right.point_count}")
        if left.triangle_count != right.triangle_count:
            differences.append(f"triangle count differs: {left.triangle_count} != {right.triangle_count}")

        left_points = {point.point_id: point for point in left.points}
        right_points = {point.point_id: point for point in right.points}
        for point_id, point in left_points.items():
            other = right_points.get(point_id)
            if other is None:
                differences.append(f"missing point: {point_id}")
                continue
            for axis in ("x", "y", "z"):
                if abs(getattr(point, axis) - getattr(other, axis)) > tolerance:
                    differences.append(f"point {point_id} {axis} differs")
        if {tuple(sorted(triangle.point_ids)) for triangle in left.triangles} != {tuple(sorted(triangle.point_ids)) for triangle in right.triangles}:
            differences.append("triangle topology differs")
        return FormatComparison(matches=not differences, differences=differences)
