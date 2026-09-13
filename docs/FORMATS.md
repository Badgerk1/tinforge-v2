# Format Specifications

TinForge v2 includes deterministic exporters for Topcon-style TP3, Leica-style DBX, LandXML, DXF, and ASCII/CSV output. The binary TP3 and DBX implementations expose explicit headers, metadata blocks, point records, and triangle records so reference parsing and validation can be automated in tests.
