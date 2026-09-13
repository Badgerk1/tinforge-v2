from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.app import TinForgeApp


def main() -> None:
    app = TinForgeApp()
    sample = Path("sample_points.csv")
    if not sample.exists():
        sample.write_text("point_id,x,y,z,description\n1,0,0,100,A\n2,10,0,101,B\n3,0,10,102,C\n", encoding="utf-8")
    model = app.generate_tin(sample, name="Example Surface")
    outputs = app.export(model, Path("out"))
    for export_name, output_path in outputs.items():
        print(f"{export_name}: {output_path}")


if __name__ == "__main__":
    main()
