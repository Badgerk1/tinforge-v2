# API

- `src.core.point.Point3D`: survey point model
- `src.core.triangle.Triangle`: triangle topology and geometry helpers
- `src.core.tin_model.TINModel`: full surface container
- `src.core.triangulation.DelaunayTriangulator`: triangulation service
- `src.parsers.CSVParser`, `src.parsers.PDFParser`, `src.parsers.TP3Parser`: import and reference parsing APIs
- `src.exporters.TopconTP3Exporter`, `src.exporters.LeicaDBXExporter`, `src.exporters.LandXMLExporter`, `src.exporters.DXFExporter`, `src.exporters.ASCIIExporter`: export APIs
- `src.validation.TINValidator`, `src.validation.FormatValidator`: model and format validation APIs
- `src.app.TinForgeApp`: end-to-end application facade
