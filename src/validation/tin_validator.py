from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.tin_model import TINModel


@dataclass(slots=True)
class ValidationReport:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)


class TINValidator:
    def validate(self, model: TINModel) -> ValidationReport:
        errors: list[str] = []
        warnings: list[str] = []
        lookup = model.point_lookup
        seen_triangles = set()

        if model.point_count < 3:
            errors.append("TIN must contain at least three points")
        for point in model.points:
            try:
                point.validate()
            except ValueError as exc:
                errors.append(str(exc))
        for triangle in model.triangles:
            key = tuple(sorted(triangle.point_ids))
            if key in seen_triangles:
                warnings.append(f"duplicate triangle topology detected: {key}")
            seen_triangles.add(key)
            try:
                triangle.validate_edges(lookup)
            except ValueError as exc:
                errors.append(str(exc))

        statistics = model.statistics() if model.points else {"point_count": 0, "triangle_count": 0}
        return ValidationReport(is_valid=not errors, errors=errors, warnings=warnings, statistics=statistics)
