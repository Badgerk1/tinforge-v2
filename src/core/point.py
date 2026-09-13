from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any


@dataclass(slots=True)
class Point3D:
    x: float
    y: float
    z: float
    point_id: int | None = None
    description: str = ""
    code: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        for name, value in (("x", self.x), ("y", self.y), ("z", self.z)):
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{name} must be a finite number")
        if self.point_id is not None and self.point_id < 0:
            raise ValueError("point_id must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "x": float(self.x),
            "y": float(self.y),
            "z": float(self.z),
            "point_id": self.point_id,
            "description": self.description,
            "code": self.code,
            "attributes": dict(self.attributes),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Point3D":
        point = cls(
            x=float(payload["x"]),
            y=float(payload["y"]),
            z=float(payload["z"]),
            point_id=payload.get("point_id"),
            description=payload.get("description", ""),
            code=payload.get("code", ""),
            attributes=dict(payload.get("attributes", {})),
        )
        point.validate()
        return point
