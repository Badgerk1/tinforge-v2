# Architecture

TinForge v2 uses a unified internal `TINModel` for parsed survey points, triangulation output, and exporter serialization. Parsers convert source data into `Point3D` objects, the triangulator builds `Triangle` topology, and exporters serialize the resulting model into machine-control friendly formats.
