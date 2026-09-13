# tinforge-v2

TinForge v2 is a professional TIN generation and multi-format export engine. It provides:

- Survey point models and TIN surface containers
- Delaunay triangulation with quality metrics
- CSV and PDF-style point extraction
- Deterministic TP3, DBX, LandXML, DXF, and ASCII exporters
- Validation tools for TINs and exported surfaces

## Quick start

```python
from src.app import TinForgeApp

app = TinForgeApp()
model = app.generate_tin("sample_points.csv", name="Site Surface")
outputs = app.export(model, "out")
```
